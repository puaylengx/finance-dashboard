import pytest
from unittest.mock import AsyncMock, patch

from app.core.security import create_access_token


MOCK_DASHBOARD = {
    "kpis": {"total_amount": 1000000, "total_budget": 900000000, "doc_count": 42},
    "trend_month": [],
    "table_by_gl": [],
    "table_by_cost_center": [],
}


@pytest.mark.asyncio
class TestFinanceEndpoint:
    async def test_finance_requires_auth(self, client):
        resp = await client.get("/api/v1/finance")
        assert resp.status_code == 401

    async def test_finance_requires_fa_role(self, client, division_token):
        resp = await client.get(
            "/api/v1/finance",
            headers={"Authorization": f"Bearer {division_token}"},
        )
        assert resp.status_code == 403

    async def test_finance_fa_access(self, client, auth_headers_fa):
        with patch(
            "app.services.finance_service.get_dashboard",
            AsyncMock(return_value=MOCK_DASHBOARD),
        ):
            resp = await client.get("/api/v1/finance?year=2025", headers=auth_headers_fa)
        assert resp.status_code == 200
        data = resp.json()
        assert "kpis" in data
        assert data["kpis"]["doc_count"] == 42

    async def test_finance_invalid_year(self, client, auth_headers_fa):
        resp = await client.get("/api/v1/finance?year=1999", headers=auth_headers_fa)
        assert resp.status_code == 422

    async def test_finance_invalid_month(self, client, auth_headers_fa):
        resp = await client.get("/api/v1/finance?year=2025&month_from=13", headers=auth_headers_fa)
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestBudgetEndpoint:
    async def test_budget_requires_auth(self, client):
        resp = await client.get("/api/v1/budget")
        assert resp.status_code == 401

    async def test_budget_all_roles_can_access(self, client, auth_headers_division):
        with patch(
            "app.services.finance_service.get_dashboard",
            AsyncMock(return_value=MOCK_DASHBOARD),
        ):
            resp = await client.get("/api/v1/budget?year=2025", headers=auth_headers_division)
        assert resp.status_code == 200


@pytest.mark.asyncio
class TestIOEndpoint:
    async def test_io_requires_auth(self, client):
        resp = await client.get("/api/v1/io")
        assert resp.status_code == 401

    async def test_io_all_authenticated_can_access(self, client, auth_headers_division):
        mock_io = {"kpis": {"total_amount": 500000}, "pivot_table_by_io_goods": []}
        with patch(
            "app.services.finance_service.get_io",
            AsyncMock(return_value=mock_io),
        ):
            resp = await client.get("/api/v1/io?year=2025", headers=auth_headers_division)
        assert resp.status_code == 200
        data = resp.json()
        assert "kpis" in data
