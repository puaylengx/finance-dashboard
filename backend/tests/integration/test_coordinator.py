import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from zoneinfo import ZoneInfo

from app.core.security import create_access_token

_TZ_THAI = ZoneInfo("Asia/Bangkok")

_COORD_ROW = {
    "id": 1,
    "username": "alice",
    "active": True,
    "created_at": datetime(2025, 1, 1, tzinfo=_TZ_THAI),
    "updated_at": None,
    "created_by": "admin",
    "updated_by": None,
}

_PAGINATED_EMPTY = {
    "success": True,
    "data": [],
    "page": 1,
    "page_size": 20,
    "total": 0,
    "total_pages": 0,
}

_PAGINATED_ONE = {
    "success": True,
    "data": [_COORD_ROW],
    "page": 1,
    "page_size": 20,
    "total": 1,
    "total_pages": 1,
}


@pytest.fixture
def fa_chief_token() -> str:
    return create_access_token("admin", "fa", position="chief")


@pytest.fixture
def fa_no_position_token() -> str:
    return create_access_token("admin", "fa")


@pytest.fixture
def fa_chief_headers(fa_chief_token: str) -> dict:
    return {"Authorization": f"Bearer {fa_chief_token}"}


@pytest.fixture
def fa_no_position_headers(fa_no_position_token: str) -> dict:
    return {"Authorization": f"Bearer {fa_no_position_token}"}


@pytest.mark.asyncio
class TestListCoordinators:
    async def test_requires_auth(self, client):
        resp = await client.get("/api/v1/admin/coordinators")
        assert resp.status_code == 401

    async def test_requires_fa_with_position(self, client, fa_no_position_headers):
        resp = await client.get(
            "/api/v1/admin/coordinators", headers=fa_no_position_headers
        )
        assert resp.status_code == 403

    async def test_returns_paginated_response_shape(self, client, fa_chief_headers):
        with patch(
            "app.services.coordinator_service.list_coordinators",
            AsyncMock(return_value=_PAGINATED_EMPTY),
        ):
            resp = await client.get(
                "/api/v1/admin/coordinators", headers=fa_chief_headers
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data
        assert "page" in data
        assert "page_size" in data
        assert "total" in data
        assert "total_pages" in data
        assert data["success"] is True

    async def test_default_pagination_params(self, client, fa_chief_headers):
        captured = {}

        async def mock_list(**kwargs):
            captured.update(kwargs)
            return _PAGINATED_EMPTY

        with patch(
            "app.services.coordinator_service.list_coordinators",
            side_effect=mock_list,
        ):
            await client.get("/api/v1/admin/coordinators", headers=fa_chief_headers)

        assert captured["page"] == 1
        assert captured["page_size"] == 20
        assert captured["q"] is None
        assert captured["active"] is None

    async def test_passes_q_filter(self, client, fa_chief_headers):
        captured = {}

        async def mock_list(**kwargs):
            captured.update(kwargs)
            return _PAGINATED_EMPTY

        with patch(
            "app.services.coordinator_service.list_coordinators",
            side_effect=mock_list,
        ):
            await client.get(
                "/api/v1/admin/coordinators?q=alice", headers=fa_chief_headers
            )

        assert captured["q"] == "alice"

    async def test_passes_active_filter_true(self, client, fa_chief_headers):
        captured = {}

        async def mock_list(**kwargs):
            captured.update(kwargs)
            return _PAGINATED_EMPTY

        with patch(
            "app.services.coordinator_service.list_coordinators",
            side_effect=mock_list,
        ):
            await client.get(
                "/api/v1/admin/coordinators?active=true", headers=fa_chief_headers
            )

        assert captured["active"] is True

    async def test_passes_active_filter_false(self, client, fa_chief_headers):
        captured = {}

        async def mock_list(**kwargs):
            captured.update(kwargs)
            return _PAGINATED_EMPTY

        with patch(
            "app.services.coordinator_service.list_coordinators",
            side_effect=mock_list,
        ):
            await client.get(
                "/api/v1/admin/coordinators?active=false", headers=fa_chief_headers
            )

        assert captured["active"] is False

    async def test_custom_page_and_page_size(self, client, fa_chief_headers):
        captured = {}

        async def mock_list(**kwargs):
            captured.update(kwargs)
            return _PAGINATED_EMPTY

        with patch(
            "app.services.coordinator_service.list_coordinators",
            side_effect=mock_list,
        ):
            await client.get(
                "/api/v1/admin/coordinators?page=3&page_size=5",
                headers=fa_chief_headers,
            )

        assert captured["page"] == 3
        assert captured["page_size"] == 5

    async def test_page_size_too_large_is_rejected(self, client, fa_chief_headers):
        resp = await client.get(
            "/api/v1/admin/coordinators?page_size=200", headers=fa_chief_headers
        )
        assert resp.status_code == 422

    async def test_page_zero_is_rejected(self, client, fa_chief_headers):
        resp = await client.get(
            "/api/v1/admin/coordinators?page=0", headers=fa_chief_headers
        )
        assert resp.status_code == 422

    async def test_returns_data_with_items(self, client, fa_chief_headers):
        with patch(
            "app.services.coordinator_service.list_coordinators",
            AsyncMock(return_value=_PAGINATED_ONE),
        ):
            resp = await client.get(
                "/api/v1/admin/coordinators", headers=fa_chief_headers
            )
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 1
        assert body["total_pages"] == 1
        assert len(body["data"]) == 1
        assert body["data"][0]["username"] == "alice"


@pytest.mark.asyncio
class TestAddCoordinator:
    async def test_requires_auth(self, client):
        resp = await client.post("/api/v1/admin/coordinators", json={"username": "alice"})
        assert resp.status_code == 401

    async def test_requires_fa_with_position(self, client, fa_no_position_headers):
        resp = await client.post(
            "/api/v1/admin/coordinators",
            json={"username": "alice"},
            headers=fa_no_position_headers,
        )
        assert resp.status_code == 403

    async def test_success_returns_201(self, client, fa_chief_headers):
        with patch(
            "app.services.coordinator_service.add_coordinator",
            AsyncMock(return_value=_COORD_ROW),
        ):
            resp = await client.post(
                "/api/v1/admin/coordinators",
                json={"username": "alice"},
                headers=fa_chief_headers,
            )
        assert resp.status_code == 201
        body = resp.json()
        assert body["success"] is True
        assert body["data"]["username"] == "alice"

    async def test_passes_username_and_caller(self, client, fa_chief_headers):
        captured = {}

        async def mock_add(**kwargs):
            captured.update(kwargs)
            return _COORD_ROW

        with patch("app.services.coordinator_service.add_coordinator", side_effect=mock_add):
            await client.post(
                "/api/v1/admin/coordinators",
                json={"username": "bob"},
                headers=fa_chief_headers,
            )

        assert captured["username"] == "bob"
        assert captured["created_by"] == "admin"

    async def test_invalid_username_rejected(self, client, fa_chief_headers):
        resp = await client.post(
            "/api/v1/admin/coordinators",
            json={"username": "bad username!"},
            headers=fa_chief_headers,
        )
        assert resp.status_code == 422

    async def test_empty_username_rejected(self, client, fa_chief_headers):
        resp = await client.post(
            "/api/v1/admin/coordinators",
            json={"username": ""},
            headers=fa_chief_headers,
        )
        assert resp.status_code == 422

    async def test_service_error_returns_500(self, client, fa_chief_headers):
        with patch(
            "app.services.coordinator_service.add_coordinator",
            AsyncMock(side_effect=RuntimeError("db error")),
        ):
            resp = await client.post(
                "/api/v1/admin/coordinators",
                json={"username": "alice"},
                headers=fa_chief_headers,
            )
        assert resp.status_code == 500


@pytest.mark.asyncio
class TestToggleCoordinator:
    async def test_requires_auth(self, client):
        resp = await client.patch("/api/v1/admin/coordinators/1")
        assert resp.status_code == 401

    async def test_requires_fa_with_position(self, client, fa_no_position_headers):
        resp = await client.patch(
            "/api/v1/admin/coordinators/1", headers=fa_no_position_headers
        )
        assert resp.status_code == 403

    async def test_success_returns_200_with_updated_record(self, client, fa_chief_headers):
        toggled = {**_COORD_ROW, "active": False}
        with patch(
            "app.services.coordinator_service.toggle_coordinator",
            AsyncMock(return_value=toggled),
        ):
            resp = await client.patch(
                "/api/v1/admin/coordinators/1", headers=fa_chief_headers
            )
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["data"]["active"] is False

    async def test_not_found_returns_404(self, client, fa_chief_headers):
        with patch(
            "app.services.coordinator_service.toggle_coordinator",
            AsyncMock(return_value=None),
        ):
            resp = await client.patch(
                "/api/v1/admin/coordinators/999", headers=fa_chief_headers
            )
        assert resp.status_code == 404

    async def test_service_error_returns_500(self, client, fa_chief_headers):
        with patch(
            "app.services.coordinator_service.toggle_coordinator",
            AsyncMock(side_effect=RuntimeError("db error")),
        ):
            resp = await client.patch(
                "/api/v1/admin/coordinators/1", headers=fa_chief_headers
            )
        assert resp.status_code == 500


@pytest.mark.asyncio
class TestListCoordinatorsErrors:
    async def test_service_error_returns_500(self, client, fa_chief_headers):
        with patch(
            "app.services.coordinator_service.list_coordinators",
            AsyncMock(side_effect=RuntimeError("db down")),
        ):
            resp = await client.get(
                "/api/v1/admin/coordinators", headers=fa_chief_headers
            )
        assert resp.status_code == 500


@pytest.mark.asyncio
class TestCoordinatorServicePagination:
    """Unit tests for list_coordinators SQL-level pagination logic."""

    def _make_mock_db(self, total: int, rows: list[tuple], col_names: list[str]):
        mock_cur = AsyncMock()
        mock_cur.fetchone = AsyncMock(return_value=(total,))
        mock_cur.fetchall = AsyncMock(return_value=rows)
        mock_cur.execute = AsyncMock()

        from collections import namedtuple
        ColDesc = namedtuple("ColDesc", ["name"])
        mock_cur.description = [ColDesc(name=n) for n in col_names]

        mock_cur.__aenter__ = AsyncMock(return_value=mock_cur)
        mock_cur.__aexit__ = AsyncMock(return_value=False)

        mock_conn = MagicMock()
        mock_conn.cursor = MagicMock(return_value=mock_cur)
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=False)

        return mock_conn, mock_cur

    async def test_total_pages_calculation(self):
        from app.services.coordinator_service import list_coordinators

        col_names = ["id", "username", "active", "created_at", "updated_at", "created_by", "updated_by"]
        mock_conn, mock_cur = self._make_mock_db(total=45, rows=[], col_names=col_names)

        with patch("app.services.coordinator_service.get_admin_db") as mock_get_db:
            mock_get_db.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_get_db.return_value.__aexit__ = AsyncMock(return_value=False)
            result = await list_coordinators(page=1, page_size=20)

        assert result["total"] == 45
        assert result["total_pages"] == 3  # ceil(45/20)

    async def test_offset_calculated_correctly(self):
        from app.services.coordinator_service import list_coordinators

        col_names = ["id", "username", "active", "created_at", "updated_at", "created_by", "updated_by"]
        mock_conn, mock_cur = self._make_mock_db(total=50, rows=[], col_names=col_names)
        execute_calls = []
        mock_cur.execute = AsyncMock(side_effect=lambda sql, params=None: execute_calls.append((sql, params)))
        mock_cur.fetchone = AsyncMock(return_value=(50,))
        mock_cur.fetchall = AsyncMock(return_value=[])

        with patch("app.services.coordinator_service.get_admin_db") as mock_get_db:
            mock_get_db.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_get_db.return_value.__aexit__ = AsyncMock(return_value=False)
            await list_coordinators(page=3, page_size=10)

        # The second execute call is the SELECT with LIMIT/OFFSET
        _, params = execute_calls[1]
        assert params["limit"] == 10
        assert params["offset"] == 20  # (3-1) * 10

    async def test_q_filter_adds_ilike_param(self):
        from app.services.coordinator_service import list_coordinators

        col_names = ["id", "username", "active", "created_at", "updated_at", "created_by", "updated_by"]
        mock_conn, mock_cur = self._make_mock_db(total=0, rows=[], col_names=col_names)
        execute_calls = []
        mock_cur.execute = AsyncMock(side_effect=lambda sql, params=None: execute_calls.append((sql, params)))
        mock_cur.fetchone = AsyncMock(return_value=(0,))
        mock_cur.fetchall = AsyncMock(return_value=[])

        with patch("app.services.coordinator_service.get_admin_db") as mock_get_db:
            mock_get_db.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_get_db.return_value.__aexit__ = AsyncMock(return_value=False)
            await list_coordinators(q="alice")

        _, params = execute_calls[0]
        assert params.get("q") == "%alice%"

    async def test_active_filter_included_in_params(self):
        from app.services.coordinator_service import list_coordinators

        col_names = ["id", "username", "active", "created_at", "updated_at", "created_by", "updated_by"]
        mock_conn, mock_cur = self._make_mock_db(total=0, rows=[], col_names=col_names)
        execute_calls = []
        mock_cur.execute = AsyncMock(side_effect=lambda sql, params=None: execute_calls.append((sql, params)))
        mock_cur.fetchone = AsyncMock(return_value=(0,))
        mock_cur.fetchall = AsyncMock(return_value=[])

        with patch("app.services.coordinator_service.get_admin_db") as mock_get_db:
            mock_get_db.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_get_db.return_value.__aexit__ = AsyncMock(return_value=False)
            await list_coordinators(active=False)

        _, params = execute_calls[0]
        assert params.get("active") is False

    async def test_no_filters_uses_empty_where(self):
        from app.services.coordinator_service import list_coordinators

        col_names = ["id", "username", "active", "created_at", "updated_at", "created_by", "updated_by"]
        mock_conn, mock_cur = self._make_mock_db(total=0, rows=[], col_names=col_names)
        execute_calls = []
        mock_cur.execute = AsyncMock(side_effect=lambda sql, params=None: execute_calls.append((sql, params)))
        mock_cur.fetchone = AsyncMock(return_value=(0,))
        mock_cur.fetchall = AsyncMock(return_value=[])

        with patch("app.services.coordinator_service.get_admin_db") as mock_get_db:
            mock_get_db.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_get_db.return_value.__aexit__ = AsyncMock(return_value=False)
            await list_coordinators()

        count_sql, _ = execute_calls[0]
        assert "WHERE" not in count_sql
