import json
import pytest
from unittest.mock import AsyncMock, patch

from app.services.cache_service import (
    get_cached,
    set_cached,
    invalidate_pattern,
    invalidate_coordinator_cache,
)


@pytest.fixture
def redis():
    return AsyncMock()


class TestGetCached:
    async def test_returns_none_when_redis_unavailable(self):
        with patch("app.services.cache_service.get_redis", return_value=None):
            assert await get_cached("some:key") is None

    async def test_returns_none_on_cache_miss(self, redis):
        redis.get = AsyncMock(return_value=None)
        with patch("app.services.cache_service.get_redis", return_value=redis):
            assert await get_cached("missing:key") is None

    async def test_returns_parsed_dict_on_hit(self, redis):
        data = {"kpis": {"total": 42}, "trend": []}
        redis.get = AsyncMock(return_value=json.dumps(data).encode())
        with patch("app.services.cache_service.get_redis", return_value=redis):
            result = await get_cached("hit:key")
        assert result == data

    async def test_returns_parsed_list_on_hit(self, redis):
        data = [{"id": 1}, {"id": 2}]
        redis.get = AsyncMock(return_value=json.dumps(data).encode())
        with patch("app.services.cache_service.get_redis", return_value=redis):
            result = await get_cached("list:key")
        assert result == data

    async def test_returns_none_on_redis_error(self, redis):
        redis.get = AsyncMock(side_effect=Exception("connection refused"))
        with patch("app.services.cache_service.get_redis", return_value=redis):
            assert await get_cached("error:key") is None


class TestSetCached:
    async def test_no_op_when_redis_unavailable(self):
        with patch("app.services.cache_service.get_redis", return_value=None):
            await set_cached("key", {"data": 1}, ttl=60)  # should not raise

    async def test_stores_json_with_correct_key_and_ttl(self, redis):
        redis.setex = AsyncMock()
        with patch("app.services.cache_service.get_redis", return_value=redis):
            await set_cached("test:key", {"val": 99}, ttl=300)

        redis.setex.assert_called_once()
        key, ttl, raw = redis.setex.call_args[0]
        assert key == "test:key"
        assert ttl == 300
        assert json.loads(raw) == {"val": 99}

    async def test_stores_list_value(self, redis):
        redis.setex = AsyncMock()
        with patch("app.services.cache_service.get_redis", return_value=redis):
            await set_cached("list:key", [1, 2, 3], ttl=60)

        _, _, raw = redis.setex.call_args[0]
        assert json.loads(raw) == [1, 2, 3]

    async def test_silently_handles_redis_error(self, redis):
        redis.setex = AsyncMock(side_effect=Exception("redis down"))
        with patch("app.services.cache_service.get_redis", return_value=redis):
            await set_cached("key", {}, ttl=60)  # should not raise


class TestInvalidatePattern:
    async def test_returns_zero_when_redis_unavailable(self):
        with patch("app.services.cache_service.get_redis", return_value=None):
            assert await invalidate_pattern("seamless:*") == 0

    async def test_returns_zero_when_no_keys_match(self, redis):
        redis.keys = AsyncMock(return_value=[])
        with patch("app.services.cache_service.get_redis", return_value=redis):
            assert await invalidate_pattern("seamless:missing:*") == 0
        redis.delete.assert_not_called()

    async def test_deletes_all_matching_keys_and_returns_count(self, redis):
        redis.keys = AsyncMock(return_value=["key1", "key2", "key3"])
        redis.delete = AsyncMock(return_value=3)
        with patch("app.services.cache_service.get_redis", return_value=redis):
            count = await invalidate_pattern("key*")
        assert count == 3
        redis.delete.assert_called_once_with("key1", "key2", "key3")

    async def test_returns_zero_on_redis_error(self, redis):
        redis.keys = AsyncMock(side_effect=Exception("timeout"))
        with patch("app.services.cache_service.get_redis", return_value=redis):
            assert await invalidate_pattern("*") == 0


class TestInvalidateCoordinatorCache:
    async def test_queries_correct_pattern_for_username(self, redis):
        redis.keys = AsyncMock(return_value=[])
        with patch("app.services.cache_service.get_redis", return_value=redis):
            await invalidate_coordinator_cache("alice")
        redis.keys.assert_called_once_with("seamless:coordinator:alice")

    async def test_deletes_matched_coordinator_key(self, redis):
        target = "seamless:coordinator:bob"
        redis.keys = AsyncMock(return_value=[target])
        redis.delete = AsyncMock(return_value=1)
        with patch("app.services.cache_service.get_redis", return_value=redis):
            await invalidate_coordinator_cache("bob")
        redis.delete.assert_called_once_with(target)

    async def test_no_op_when_no_cache_entry(self, redis):
        redis.keys = AsyncMock(return_value=[])
        with patch("app.services.cache_service.get_redis", return_value=redis):
            await invalidate_coordinator_cache("nobody")
        redis.delete.assert_not_called()
