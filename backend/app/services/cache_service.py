import json
from typing import Any

from app.core.logging import get_logger
from app.core.redis_client import get_redis

logger = get_logger(__name__)


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
    await invalidate_pattern(f"seamless:coordinator:{username}")
