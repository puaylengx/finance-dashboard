import json

import bcrypt
import httpx
from jose import JWTError, jwt as jose_jwt

from app.core.config import settings
from app.core.database import get_db
from app.core.logging import get_logger
from app.core.redis_client import get_redis
from app.core.security import (
    create_access_token,
    extract_claims,
    has_access_by_position,
)
from app.schemas.auth import TokenResponse

logger = get_logger(__name__)

_entra_jwks_cache: dict | None = None


class EntraNotConfiguredError(Exception):
    """Raised when MS Entra ID credentials are missing from settings."""


def _load_users() -> list[dict]:
    try:
        return json.loads(settings.auth_users_json)
    except json.JSONDecodeError:
        logger.error("AUTH_USERS_JSON is not valid JSON")
        return []


async def is_coordinator(username: str) -> bool:
    """Return True if username is active in finance_coordinator. Cached in Redis."""
    redis = get_redis()
    cache_key = f"seamless:coordinator:{username}"

    if redis:
        try:
            cached = await redis.get(cache_key)
            if cached is not None:
                return cached == "1"
        except Exception:
            pass

    result = False
    try:
        async with get_db() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT 1 FROM finance_coordinator WHERE username = %(username)s AND active = TRUE",
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
    global _entra_jwks_cache
    if _entra_jwks_cache:
        return _entra_jwks_cache

    jwks_url = (
        f"https://login.microsoftonline.com/{settings.azure_tenant_id}"
        f"/discovery/v2.0/keys"
    )
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(jwks_url)
        resp.raise_for_status()
        _entra_jwks_cache = resp.json()
    return _entra_jwks_cache


async def login_with_entra_token(access_token: str) -> TokenResponse | None:
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
            audience=settings.azure_client_id,
        )
    except (JWTError, httpx.HTTPError, StopIteration) as exc:
        logger.warning("Entra token validation failed: %s", exc)
        return None

    job_title: str = claims.get("jobTitle") or claims.get("job_title") or ""
    display_name: str = claims.get("name") or claims.get("displayName") or ""
    username: str = claims.get("preferred_username") or claims.get("upn") or display_name

    extracted = extract_claims(job_title)
    role = extracted["role"]
    position = extracted["position"]

    if has_access_by_position(position):
        token = create_access_token(username, role, position=position)
        logger.info("Entra login (position): %s → role=%s pos=%s", username, role, position)
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
        logger.info("Entra login (coordinator): %s → role=%s", username, role)
        return TokenResponse(
            token=token,
            expires_in=settings.jwt_expires_seconds,
            role=role,
            coordinator=True,
            name=display_name,
        )

    logger.warning("Entra login denied: %s (job_title='%s')", username, job_title)
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
