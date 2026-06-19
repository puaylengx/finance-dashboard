"""Circuit breaker tests for Azure JWKS fetch in auth_service."""
import time
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

import app.services.auth_service as svc


def _reset_circuit():
    svc._entra_jwks_cache = None
    svc._jwks_failure_count = 0
    svc._jwks_circuit_open_until = 0.0


@pytest.fixture(autouse=True)
def reset_state():
    _reset_circuit()
    yield
    _reset_circuit()


class TestJwksCircuitBreaker:
    @pytest.mark.asyncio
    async def test_success_resets_failure_count(self):
        svc._jwks_failure_count = 2
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"keys": []}

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_resp)
            await svc._fetch_entra_jwks()

        assert svc._jwks_failure_count == 0

    @pytest.mark.asyncio
    async def test_single_failure_increments_count(self):
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=httpx.ConnectError("connection refused")
            )
            with pytest.raises(httpx.HTTPError):
                await svc._fetch_entra_jwks()

        assert svc._jwks_failure_count == 1
        assert svc._jwks_circuit_open_until == 0.0  # circuit still closed

    @pytest.mark.asyncio
    async def test_threshold_failures_open_circuit(self):
        svc._jwks_failure_count = svc._JWKS_FAILURE_THRESHOLD - 1

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=httpx.ConnectError("connection refused")
            )
            with pytest.raises(svc.EntraNotConfiguredError):
                await svc._fetch_entra_jwks()

        assert svc._jwks_circuit_open_until > time.monotonic()
        assert svc._jwks_failure_count == 0  # reset after opening

    @pytest.mark.asyncio
    async def test_open_circuit_fails_fast_without_http_call(self):
        svc._jwks_circuit_open_until = time.monotonic() + 60

        called = []
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=lambda *a, **kw: called.append(1)
            )
            with pytest.raises(svc.EntraNotConfiguredError, match="retry in"):
                await svc._fetch_entra_jwks()

        assert len(called) == 0  # no HTTP call made

    @pytest.mark.asyncio
    async def test_circuit_recovers_after_cooldown(self):
        svc._jwks_circuit_open_until = time.monotonic() - 1  # cooldown expired
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"keys": []}

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_resp)
            result = await svc._fetch_entra_jwks()

        assert result == {"keys": []}

    @pytest.mark.asyncio
    async def test_cached_jwks_bypasses_circuit(self):
        svc._entra_jwks_cache = {"keys": ["cached"]}
        svc._jwks_circuit_open_until = time.monotonic() + 999

        result = await svc._fetch_entra_jwks()
        assert result == {"keys": ["cached"]}
