from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.core.cache import auth_blacklist_key
from app.core.redis_client import get_redis
from app.core.security import FA_ROLES, decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Decode and validate JWT. Returns the token payload dict."""
    try:
        payload = decode_access_token(token)
        if not payload.get("sub"):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

        jti = payload.get("jti")
        if jti:
            redis = get_redis()
            if redis and await redis.exists(auth_blacklist_key(jti)):
                raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")

        return payload
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def require_fa(user: dict = Depends(get_current_user)) -> dict:
    """Require FA (finance admin) role."""
    if user.get("role", "").lower() not in FA_ROLES:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Requires FA role")
    return user


async def require_fa_with_position(user: dict = Depends(get_current_user)) -> dict:
    """Require FA role AND a position (chief/chairman/head) — for coordinator management."""
    if user.get("role", "").lower() not in FA_ROLES or not user.get("position"):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="Access restricted to FA with a position",
        )
    return user
