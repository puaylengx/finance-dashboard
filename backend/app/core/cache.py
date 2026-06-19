import json
from typing import Any

from app.core.logging import get_logger
from app.core.redis_client import get_redis

logger = get_logger(__name__)

_AUTH_COORDINATOR_PREFIX = "seamless:v1:auth:coordinator"
_AUTH_BLACKLIST_PREFIX = "seamless:v1:auth:blacklist"
_FINANCE_PREFIX = "seamless:v1:finance"


def auth_coordinator_key(username: str) -> str:
    return f"{_AUTH_COORDINATOR_PREFIX}:{username}"


def auth_blacklist_key(jti: str) -> str:
    return f"{_AUTH_BLACKLIST_PREFIX}:{jti}"


def finance_cache_key(prefix: str, role: str, params_hash: str) -> str:
    return f"{_FINANCE_PREFIX}:{prefix}:{role}:{params_hash}"


async def get_cached(key: str) -> Any | None:
    redis = get_redis()
    if redis is None:
        return None
    try:
        raw = await redis.get(key)
        if raw is not None:
            logger.debug("Cache HIT: %s", key)
            return json.loads(raw)
    except Exception as exc:
        logger.warning("Cache get error: %s", exc)
    return None


async def set_cached(key: str, value: Any, ttl: int) -> None:
    redis = get_redis()
    if redis is None:
        return
    try:
        await redis.setex(key, ttl, json.dumps(value, default=str))
        logger.debug("Cache SET: %s (ttl=%ds)", key, ttl)
    except Exception as exc:
        logger.warning("Cache set error: %s", exc)


async def invalidate_pattern(pattern: str) -> int:
    redis = get_redis()
    if redis is None:
        return 0
    try:
        keys = await redis.keys(pattern)
        if keys:
            deleted = await redis.delete(*keys)
            logger.info("Cache invalidated %d keys matching '%s'", deleted, pattern)
            return deleted
    except Exception as exc:
        logger.warning("Cache invalidate error: %s", exc)
    return 0


async def invalidate_coordinator_cache(username: str) -> None:
    await invalidate_pattern(auth_coordinator_key(username))


# ── Idempotency ───────────────────────────────────────────────────────────────

_IDEMPOTENCY_PREFIX = "seamless:v1:idempotency"
_IDEMPOTENCY_TTL = 86_400  # 24 hours


def idempotency_cache_key(user_id: str, key: str) -> str:
    return f"{_IDEMPOTENCY_PREFIX}:{user_id}:{key}"


async def get_idempotency_response(user_id: str, key: str) -> dict | None:
    return await get_cached(idempotency_cache_key(user_id, key))


async def set_idempotency_response(user_id: str, key: str, response: dict) -> None:
    await set_cached(idempotency_cache_key(user_id, key), response, _IDEMPOTENCY_TTL)
