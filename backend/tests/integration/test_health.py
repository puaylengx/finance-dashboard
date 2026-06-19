import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
class TestHealthEndpoint:
    async def test_health_returns_ok(self, client):
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "version" in data


@pytest.mark.asyncio
class TestReadinessEndpoint:
    def _make_db_mock(self):
        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock()
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=False)

        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_ctx.__aexit__ = AsyncMock(return_value=False)
        return mock_ctx

    async def test_ready_all_healthy(self, client):
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(return_value=True)

        with patch("app.main.get_db", return_value=self._make_db_mock()), \
             patch("app.main.get_redis", return_value=mock_redis):
            resp = await client.get("/ready")

        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    async def test_ready_db_failure_returns_503(self, client):
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(side_effect=Exception("connection refused"))
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(return_value=True)

        with patch("app.main.get_db", return_value=mock_ctx), \
             patch("app.main.get_redis", return_value=mock_redis):
            resp = await client.get("/ready")

        assert resp.status_code == 503
        data = resp.json()
        assert data["status"] == "unavailable"
        assert "db" in data["failing"]
        assert "redis" not in data["failing"]

    async def test_ready_redis_none_returns_503(self, client):
        with patch("app.main.get_db", return_value=self._make_db_mock()), \
             patch("app.main.get_redis", return_value=None):
            resp = await client.get("/ready")

        assert resp.status_code == 503
        data = resp.json()
        assert "redis" in data["failing"]
        assert "db" not in data["failing"]

    async def test_ready_redis_ping_failure_returns_503(self, client):
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(side_effect=Exception("timeout"))

        with patch("app.main.get_db", return_value=self._make_db_mock()), \
             patch("app.main.get_redis", return_value=mock_redis):
            resp = await client.get("/ready")

        assert resp.status_code == 503
        data = resp.json()
        assert "redis" in data["failing"]

    async def test_ready_both_fail_returns_503_with_both(self, client):
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(side_effect=Exception("db down"))
        mock_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch("app.main.get_db", return_value=mock_ctx), \
             patch("app.main.get_redis", return_value=None):
            resp = await client.get("/ready")

        assert resp.status_code == 503
        data = resp.json()
        assert set(data["failing"]) == {"db", "redis"}
