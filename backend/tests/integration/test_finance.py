import pytest
from unittest.mock import AsyncMock, patch

from app.core.security import create_access_token


def _mock_dashboard(rows: int = 0):
    gl_rows = [{"gl_id": i, "total": i * 100} for i in range(rows)]
    cc_rows = [{"cost_center_description": f"CC{i}", "total": i * 50} for i in range(rows)]
    return {
        "kpis": {"total_amount": 1000000, "total_budget": 900000000, "doc_count": 42},
        "trend_month": [],
        "table_by_gl": gl_rows,
        "table_by_cost_center": cc_rows,
        "table_by_gl_all": list(gl_rows),
        "table_by_cost_center_all": list(cc_rows),
        "table_by_gl_division": list(gl_rows),
        "table_by_cost_center_division": list(cc_rows),
        "pivot_table_by_gl_detail": [],
        "pivot_table_by_gl_detail_division": [],
        "pivot_table_by_gl_detail_all": [],
    }

MOCK_DASHBOARD = _mock_dashboard()


@pytest.mark.asyncio
class TestFinanceEndpoint:
    async def test_finance_requires_auth(self, client):
        resp = await client.get("/api/v1/budget")
        assert resp.status_code == 401

    async def test_finance_requires_fa_role(self, client, division_token):
        resp = await client.get(
            "/api/v1/budget",
            headers={"Authorization": f"Bearer {division_token}"},
        )
        assert resp.status_code == 403

    async def test_finance_fa_access(self, client, auth_headers_fa):
        with patch(
            "app.services.finance_service.get_dashboard",
            AsyncMock(return_value=MOCK_DASHBOARD),
        ):
            resp = await client.get("/api/v1/budget?year=2025", headers=auth_headers_fa)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "kpis" in data["data"]
        assert data["data"]["kpis"]["doc_count"] == 42

    async def test_finance_invalid_year(self, client, auth_headers_fa):
        resp = await client.get("/api/v1/budget?year=1999", headers=auth_headers_fa)
        assert resp.status_code == 422

    async def test_finance_invalid_month(self, client, auth_headers_fa):
        resp = await client.get("/api/v1/budget?year=2025&month_from=13", headers=auth_headers_fa)
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
class TestFinanceErrors:
    async def test_finance_service_error_returns_500(self, client, auth_headers_fa):
        with patch(
            "app.services.finance_service.get_dashboard",
            AsyncMock(side_effect=RuntimeError("db down")),
        ):
            resp = await client.get("/api/v1/budget?year=2025", headers=auth_headers_fa)
        assert resp.status_code == 500

    async def test_budget_service_error_returns_500(self, client, auth_headers_division):
        with patch(
            "app.services.finance_service.get_dashboard",
            AsyncMock(side_effect=RuntimeError("db down")),
        ):
            resp = await client.get("/api/v1/budget?year=2025", headers=auth_headers_division)
        assert resp.status_code == 500

    async def test_io_service_error_returns_500(self, client, auth_headers_division):
        with patch(
            "app.services.finance_service.get_io",
            AsyncMock(side_effect=RuntimeError("db down")),
        ):
            resp = await client.get("/api/v1/io?year=2025", headers=auth_headers_division)
        assert resp.status_code == 500


@pytest.mark.asyncio
class TestFinanceTopN:
    async def test_top_n_invalid_zero(self, client, auth_headers_fa):
        resp = await client.get("/api/v1/budget?year=2025&top_n=0", headers=auth_headers_fa)
        assert resp.status_code == 422

    async def test_top_n_too_large(self, client, auth_headers_fa):
        resp = await client.get("/api/v1/budget?year=2025&top_n=501", headers=auth_headers_fa)
        assert resp.status_code == 422

    async def test_top_n_limits_table_rows(self, client, auth_headers_fa):
        with patch(
            "app.services.finance_service.get_dashboard",
            AsyncMock(return_value=_mock_dashboard(rows=30)),
        ):
            resp = await client.get(
                "/api/v1/budget?year=2025&top_n=5", headers=auth_headers_fa
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert len(data["data"]["table_by_gl"]) == 5
        assert len(data["data"]["table_by_cost_center"]) == 5

    async def test_budget_top_n_limits_table_rows(self, client, auth_headers_division):
        with patch(
            "app.services.finance_service.get_dashboard",
            AsyncMock(return_value=_mock_dashboard(rows=20)),
        ):
            resp = await client.get(
                "/api/v1/budget?year=2025&top_n=3", headers=auth_headers_division
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert len(data["data"]["table_by_gl"]) == 3


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
        assert data["success"] is True
        assert "kpis" in data["data"]

    async def test_io_top_n_limits_table_rows(self, client, auth_headers_division):
        rows = [{"cost_center_description": f"CC{i}", "total": i} for i in range(25)]
        mock_io = {
            "kpis": {"total_amount": 500000},
            "spending_by_dept": list(rows),
            "spending_by_division": list(rows),
            "pivot_table_by_io_goods": list(rows),
            "pivot_table_by_io_project": list(rows),
            "pivot_table_by_io_work": list(rows),
        }
        with patch(
            "app.services.finance_service.get_io",
            AsyncMock(return_value=mock_io),
        ):
            resp = await client.get(
                "/api/v1/io?year=2025&top_n=4", headers=auth_headers_division
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert len(data["data"]["spending_by_dept"]) == 4
        assert len(data["data"]["pivot_table_by_io_goods"]) == 4

    async def test_io_top_n_invalid(self, client, auth_headers_division):
        resp = await client.get("/api/v1/io?year=2025&top_n=0", headers=auth_headers_division)
        assert resp.status_code == 422
