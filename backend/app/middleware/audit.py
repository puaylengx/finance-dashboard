import asyncio

from fastapi import Request
from jose import JWTError

from app.core.database import get_db
from app.core.logging import get_logger
from app.core.security import decode_access_token

logger = get_logger(__name__)

_SKIP_PATHS = frozenset({"/health", "/ready", "/api/docs", "/api/redoc", "/api/openapi.json"})


async def _write_audit(
    user_id: str,
    action: str,
    resource: str | None,
    ip: str | None,
    status_code: int,
) -> None:
    try:
        async with get_db() as conn:
            await conn.execute(
                "INSERT INTO audit_log (user_id, action, resource, ip_address, status_code) "
                "VALUES (%(user_id)s, %(action)s, %(resource)s, %(ip)s::inet, %(status)s)",
                {"user_id": user_id, "action": action, "resource": resource, "ip": ip, "status": status_code},
            )
    except Exception as exc:
        logger.warning("Audit log write failed: %s", exc)


async def audit_log_middleware(request: Request, call_next):
    response = await call_next(request)

    if request.url.path in _SKIP_PATHS:
        return response

    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return response

    try:
        payload = decode_access_token(auth.removeprefix("Bearer "))
        user_id = payload.get("sub", "unknown")
    except JWTError:
        return response

    action = f"{request.method} {request.url.path}"
    resource = str(request.url.query) or None
    ip = request.client.host if request.client else None

    asyncio.create_task(_write_audit(user_id, action, resource, ip, response.status_code))

    return response
