import json
import time

import bcrypt
import httpx
from jose import JWTError, jwt as jose_jwt

from app.core.cache import auth_coordinator_key
from app.core.config import settings
from app.core.database import get_auth_db
from app.core.logging import get_logger
from app.core.redis_client import get_redis
from app.core.security import (
    create_access_token,
    extract_claims,
    has_access_by_position,
)
from app.schemas.auth import TokenResponse

__all__ = [
    "EntraNotConfiguredError",
    "is_coordinator",
    "login_with_password",
    "login_with_entra_token",
    "draft_login",
]

logger = get_logger(__name__)

_entra_jwks_cache: dict | None = None
_graph_token_cache: dict | None = None
_jwks_failure_count: int = 0
_jwks_circuit_open_until: float = 0.0
_JWKS_FAILURE_THRESHOLD: int = 3
_JWKS_COOLDOWN_SECONDS: int = 60


class EntraNotConfiguredError(Exception):
    """Raised when MS Entra ID credentials are missing or circuit is open."""


def _load_users() -> list[dict]:
    try:
        return json.loads(settings.auth_users_json)
    except json.JSONDecodeError:
        logger.error("AUTH_USERS_JSON is not valid JSON")
        return []


async def is_coordinator(username: str) -> bool:
    """Return True if username is active in finance_coordinator. Cached in Redis.

    username is the raw preferred_username from Entra (full UPN) or a local name
    for draft login. Matches on upn column first, falls back to username column.
    """
    redis = get_redis()
    cache_key = auth_coordinator_key(username.lower())

    if redis:
        try:
            cached = await redis.get(cache_key)
            if cached is not None:
                return cached == "1"
        except Exception:
            pass

    result = False
    try:
        async with get_auth_db() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT 1 FROM finance_coordinator
                    WHERE (
                        LOWER(upn)      = LOWER(%(username)s)
                        OR LOWER(username) = LOWER(%(username)s)
                    ) AND active = TRUE
                    """,
                    {"username": username},
                )
                result = await cur.fetchone() is not None
    except Exception as exc:
        logger.warning("Coordinator lookup failed: %s", exc)

    if redis:
        try:
            await redis.setex(cache_key, settings.redis_ttl_coordinator, "1" if result else "0")
        except Exception:
            pass

    return result


async def login_with_password(username: str, password: str) -> TokenResponse | None:
    """Validate local credentials and issue JWT."""
    users = _load_users()
    user = next((u for u in users if u.get("username") == username), None)
    if not user:
        logger.warning("Login failed: unknown user '%s'", username)
        return None

    pw_hash = user.get("password_hash", "").encode()
    if not bcrypt.checkpw(password.encode(), pw_hash):
        logger.warning("Login failed: bad password for '%s'", username)
        return None

    role = user.get("role", "user")
    display_name = user.get("name", username)
    token = create_access_token(username, role)
    logger.info("Password login OK: %s (role=%s)", username, role)
    return TokenResponse(
        token=token,
        expires_in=settings.jwt_expires_seconds,
        role=role,
        name=display_name,
    )


async def _fetch_entra_jwks() -> dict:
    global _entra_jwks_cache, _jwks_failure_count, _jwks_circuit_open_until

    if _entra_jwks_cache:
        return _entra_jwks_cache

    # Circuit breaker: fail fast while cooldown is active
    now = time.monotonic()
    if now < _jwks_circuit_open_until:
        remaining = int(_jwks_circuit_open_until - now)
        logger.warning("Azure JWKS circuit open — fast fail, retry in %ds", remaining)
        raise EntraNotConfiguredError(
            f"Azure JWKS temporarily unavailable — retry in {remaining}s"
        )

    jwks_url = (
        f"https://login.microsoftonline.com/{settings.azure_tenant_id}"
        f"/discovery/v2.0/keys"
    )
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(jwks_url)
            resp.raise_for_status()
            _entra_jwks_cache = resp.json()
            _jwks_failure_count = 0
            return _entra_jwks_cache
    except httpx.HTTPError as exc:
        _jwks_failure_count += 1
        if _jwks_failure_count >= _JWKS_FAILURE_THRESHOLD:
            _jwks_circuit_open_until = time.monotonic() + _JWKS_COOLDOWN_SECONDS
            _jwks_failure_count = 0
            logger.error(
                "Azure JWKS circuit OPEN after %d failures — cooldown %ds",
                _JWKS_FAILURE_THRESHOLD, _JWKS_COOLDOWN_SECONDS,
            )
            raise EntraNotConfiguredError(
                f"Azure JWKS circuit opened after repeated failures: {exc}"
            ) from exc
        logger.warning(
            "Azure JWKS fetch failed (%d/%d): %s",
            _jwks_failure_count, _JWKS_FAILURE_THRESHOLD, exc,
        )
        raise


async def _fetch_graph_app_token() -> str:
    global _graph_token_cache
    if _graph_token_cache and _graph_token_cache["expires_at"] > time.time() + 60:
        return _graph_token_cache["access_token"]

    url = f"https://login.microsoftonline.com/{settings.azure_tenant_id}/oauth2/v2.0/token"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(url, data={
            "grant_type": "client_credentials",
            "client_id": settings.azure_client_id,
            "client_secret": settings.azure_client_secret,
            "scope": "https://graph.microsoft.com/.default",
        })
        resp.raise_for_status()
        result = resp.json()

    _graph_token_cache = {
        "access_token": result["access_token"],
        "expires_at": time.time() + result.get("expires_in", 3600),
    }
    return result["access_token"]


async def _get_job_title_from_graph(oid: str) -> str:
    """App-only: ต้องการ User.Read.All (application permission + admin consent)"""
    try:
        graph_token = await _fetch_graph_app_token()
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"https://graph.microsoft.com/v1.0/users/{oid}?$select=jobTitle",
                headers={"Authorization": f"Bearer {graph_token}"},
            )
            resp.raise_for_status()
            return resp.json().get("jobTitle") or ""
    except Exception as exc:
        logger.warning("Graph app-only jobTitle fetch failed: %s", exc)
        return ""


async def _get_job_title_obo(user_access_token: str) -> str:
    """On-Behalf-Of: แลก user token เป็น Graph token — ต้องการแค่ User.Read (delegated)"""
    if not settings.azure_client_secret:
        logger.debug("OBO skipped: AZURE_CLIENT_SECRET not set")
        return ""
    try:
        url = f"https://login.microsoftonline.com/{settings.azure_tenant_id}/oauth2/v2.0/token"
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, data={
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "client_id": settings.azure_client_id,
                "client_secret": settings.azure_client_secret,
                "assertion": user_access_token,
                "scope": "https://graph.microsoft.com/User.Read",
                "requested_token_use": "on_behalf_of",
            })
            if not resp.is_success:
                logger.warning("OBO token exchange failed: %s %s", resp.status_code, resp.text)
                return ""
            graph_token = resp.json()["access_token"]

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://graph.microsoft.com/v1.0/me?$select=jobTitle",
                headers={"Authorization": f"Bearer {graph_token}"},
            )
            if not resp.is_success:
                logger.warning("OBO Graph /me failed: %s %s", resp.status_code, resp.text)
                return ""
            return resp.json().get("jobTitle") or ""
    except Exception as exc:
        logger.warning("OBO unexpected error: %s", exc)
        return ""


async def login_with_entra_token(access_token: str, job_title: str = "") -> TokenResponse | None:
    """Validate MS Entra ID token and issue our JWT.

    Raises:
        EntraNotConfiguredError: AZURE_TENANT_ID or AZURE_CLIENT_ID not set.
    Returns:
        TokenResponse if access granted, None if access denied.
    """
    if not settings.azure_tenant_id or not settings.azure_client_id:
        raise EntraNotConfiguredError(
            "AZURE_TENANT_ID and AZURE_CLIENT_ID must be set to use MS Entra ID login. "
            "Use /api/v1/auth/draft-login for testing."
        )

    try:
        jwks = await _fetch_entra_jwks()
        unverified_header = jose_jwt.get_unverified_header(access_token)
        key = next(
            (k for k in jwks.get("keys", []) if k.get("kid") == unverified_header.get("kid")),
            None,
        )
        if not key:
            logger.warning("Entra login: no matching JWK found")
            return None

        claims = jose_jwt.decode(
            access_token,
            key,
            algorithms=["RS256"],
            options={"verify_aud": False},
        )
        valid_audiences = {settings.azure_client_id, f"api://{settings.azure_client_id}"}
        if claims.get("aud") not in valid_audiences:
            logger.warning("Entra login: invalid audience: %s", claims.get("aud"))
            return None
    except (JWTError, httpx.HTTPError, StopIteration) as exc:
        logger.warning("Entra token validation failed: %s", exc)
        return None

    job_title_from_token: str = claims.get("jobTitle") or claims.get("job_title") or ""
    display_name: str = claims.get("name") or claims.get("displayName") or ""
    username: str = claims.get("preferred_username") or claims.get("upn") or display_name

    # ลำดับความสำคัญ: token claim → OBO Graph → app-only Graph → frontend fallback
    effective_job_title = job_title_from_token
    job_title_source = "token"
    if not effective_job_title:
        effective_job_title = await _get_job_title_obo(access_token)
        if effective_job_title:
            job_title_source = "graph:obo"
    if not effective_job_title and settings.azure_client_secret:
        oid: str = claims.get("oid") or ""
        if oid:
            effective_job_title = await _get_job_title_from_graph(oid)
            if effective_job_title:
                job_title_source = "graph:app"
    if not effective_job_title and job_title:
        effective_job_title = job_title
        job_title_source = "frontend"

    logger.info("Entra job_title: user=%s source=%s job_title='%s'",
                username, job_title_source if effective_job_title else "none", effective_job_title)

    if not effective_job_title:
        logger.warning("Entra login denied: %s (job_title not found)", username)
        return None

    extracted = extract_claims(effective_job_title)
    role = extracted["role"]
    position = extracted["position"]

    if has_access_by_position(position):
        token = create_access_token(username, role, position=position)
        logger.info("Entra login OK (position): %s → role=%s pos=%s job_title='%s'",
                    username, role, position, effective_job_title)
        return TokenResponse(
            token=token,
            expires_in=settings.jwt_expires_seconds,
            role=role,
            position=position,
            coordinator=False,
            name=display_name,
        )

    if await is_coordinator(username):
        token = create_access_token(username, role, coordinator=True)
        logger.info("Entra login OK (coordinator): %s → role=%s job_title='%s'",
                    username, role, effective_job_title)
        return TokenResponse(
            token=token,
            expires_in=settings.jwt_expires_seconds,
            role=role,
            coordinator=True,
            name=display_name,
        )

    logger.warning("Entra login denied: %s (job_title='%s', role=%s — no position, not coordinator)",
                   username, effective_job_title, role)
    return None


async def draft_login(job_title: str, name: str) -> TokenResponse | None:
    """Dev/staging only: simulate Entra login with a raw job_title string."""
    extracted = extract_claims(job_title)
    role = extracted["role"]
    position = extracted["position"]

    if has_access_by_position(position):
        token = create_access_token(name, role, position=position)
        logger.info("Draft login (position): '%s' → role=%s pos=%s", job_title, role, position)
        return TokenResponse(
            token=token,
            expires_in=settings.jwt_expires_seconds,
            role=role,
            position=position,
            coordinator=False,
            name=name,
        )

    if await is_coordinator(name):
        token = create_access_token(name, role, coordinator=True)
        logger.info("Draft login (coordinator): %s → role=%s", name, role)
        return TokenResponse(
            token=token,
            expires_in=settings.jwt_expires_seconds,
            role=role,
            coordinator=True,
            name=name,
        )

    logger.warning("Draft login denied: no position and not coordinator, name=%s job_title=%s", name, job_title)
    return None
