import pytest
from unittest.mock import AsyncMock, patch

from app.core.security import create_access_token


@pytest.mark.asyncio
class TestLoginEndpoint:
    async def test_login_missing_fields(self, client):
        resp = await client.post("/api/v1/auth/login", data={})
        assert resp.status_code == 422

    async def test_login_invalid_credentials(self, client):
        with patch("app.services.auth_service.login_with_password", AsyncMock(return_value=None)):
            resp = await client.post(
                "/api/v1/auth/login",
                data={"username": "nobody", "password": "wrong"},
            )
        assert resp.status_code == 401

    async def test_login_success(self, client):
        from app.schemas.auth import TokenResponse
        mock_response = TokenResponse(
            token="test.jwt.token",
            expires_in=3600,
            role="fa",
            name="Test User",
        )
        with patch("app.services.auth_service.login_with_password", AsyncMock(return_value=mock_response)):
            resp = await client.post(
                "/api/v1/auth/login",
                data={"username": "admin", "password": "secret"},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["token"] == "test.jwt.token"
        assert data["data"]["role"] == "fa"


@pytest.mark.asyncio
class TestDraftLoginEndpoint:
    async def test_draft_login_denied(self, client):
        with patch("app.services.auth_service.draft_login", AsyncMock(return_value=None)):
            resp = await client.post(
                "/api/v1/auth/draft-login",
                json={"job_title": "dept,unknown", "name": "Nobody"},
            )
        assert resp.status_code == 403

    async def test_draft_login_success_with_position(self, client):
        from app.schemas.auth import TokenResponse
        mock_response = TokenResponse(
            token="chief.jwt.token",
            expires_in=3600,
            role="fa",
            position="chief",
            name="Chief User",
        )
        with patch("app.services.auth_service.draft_login", AsyncMock(return_value=mock_response)):
            resp = await client.post(
                "/api/v1/auth/draft-login",
                json={"job_title": "dept,fa,chief", "name": "Chief User"},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["position"] == "chief"

    async def test_draft_login_missing_body(self, client):
        resp = await client.post("/api/v1/auth/draft-login", json={})
        assert resp.status_code == 422

    async def test_draft_login_disabled_in_production(self, client):
        with patch("app.core.config.settings.draft_mode", False):
            resp = await client.post(
                "/api/v1/auth/draft-login",
                json={"job_title": "dept,fa,chief", "name": "Chief"},
            )
        assert resp.status_code == 404


@pytest.mark.asyncio
class TestEntraLoginEndpoint:
    async def test_entra_login_503_when_not_configured(self, client):
        from app.services.auth_service import EntraNotConfiguredError
        with patch(
            "app.services.auth_service.login_with_entra_token",
            AsyncMock(side_effect=EntraNotConfiguredError("not configured")),
        ):
            resp = await client.post(
                "/api/v1/auth/entra-login",
                json={"access_token": "fake.ms.token"},
            )
        assert resp.status_code == 503
        assert "Entra ID" in resp.json()["detail"]

    async def test_entra_login_403_when_access_denied(self, client):
        with patch(
            "app.services.auth_service.login_with_entra_token",
            AsyncMock(return_value=None),
        ):
            resp = await client.post(
                "/api/v1/auth/entra-login",
                json={"access_token": "fake.ms.token"},
            )
        assert resp.status_code == 403


@pytest.mark.asyncio
class TestMeEndpoint:
    async def test_me_requires_auth(self, client):
        resp = await client.get("/api/v1/auth/me")
        assert resp.status_code == 401

    async def test_me_returns_user_info(self, client):
        token = create_access_token("test_user", "fa", position="chief")
        resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["username"] == "test_user"
        assert data["data"]["role"] == "fa"
        assert data["data"]["position"] == "chief"

    async def test_me_invalid_token(self, client):
        resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert resp.status_code == 401
