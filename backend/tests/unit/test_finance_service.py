import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.schemas.finance import FinanceQueryParams, IOQueryParams
from app.services.finance_service import (
    _build_dashboard_params,
    _build_io_params,
    _run_query,
    get_dashboard,
    get_io,
)


# ── _build_dashboard_params ───────────────────────────────────────────────────

class TestBuildDashboardParams:
    def _p(self, **kwargs) -> FinanceQueryParams:
        return FinanceQueryParams(year=2025, **kwargs)

    def test_fa_role_cost_owner_is_none(self):
        result = _build_dashboard_params(self._p(), role="fa")
        assert result["cost_owner"] is None
        assert result["ea_cost_center"] is None

    def test_non_fa_role_sets_cost_owner_from_role(self):
        result = _build_dashboard_params(self._p(), role="bba")
        assert result["cost_owner"] == "BBA"

    def test_division_role_sets_ea_cost_center(self):
        result = _build_dashboard_params(self._p(), role="bba")
        assert result["ea_cost_center"] == "BBA"

    def test_non_division_non_fa_role_no_ea_cost_center(self):
        result = _build_dashboard_params(self._p(), role="hq")
        assert result["ea_cost_center"] is None
        assert result["cost_owner"] == "HQ"

    def test_cost_owner_override_takes_precedence_over_role(self):
        result = _build_dashboard_params(self._p(), role="bba", cost_owner_override="OVERRIDE")
        assert result["cost_owner"] == "OVERRIDE"

    def test_cost_center_builds_like_pattern(self):
        result = _build_dashboard_params(self._p(cost_center="HR"), role="fa")
        assert result["cost_center"] == "HR"
        assert result["cost_center_like"] == "%HR%"

    def test_no_cost_center_gives_none_for_both(self):
        result = _build_dashboard_params(self._p(), role="fa")
        assert result["cost_center"] is None
        assert result["cost_center_like"] is None

    def test_q_builds_like_pattern(self):
        result = _build_dashboard_params(self._p(q="salary"), role="fa")
        assert result["q"] == "salary"
        assert result["q_like"] == "%salary%"

    def test_no_q_gives_none(self):
        result = _build_dashboard_params(self._p(), role="fa")
        assert result["q"] is None
        assert result["q_like"] is None

    def test_ilike_root_override_for_sci_lab(self):
        result = _build_dashboard_params(self._p(), role="sci_lab")
        assert result["cost_owner_like"] == "%SCI%"

    def test_year_and_month_passed_through(self):
        result = _build_dashboard_params(
            self._p(month_from=1, month_to=6, pa_year=2024), role="fa"
        )
        assert result["year"] == 2025
        assert result["month_from"] == 1
        assert result["month_to"] == 6
        assert result["pa_year"] == 2024

    def test_empty_gl_group_becomes_none(self):
        result = _build_dashboard_params(self._p(gl_group=""), role="fa")
        assert result["gl_group"] is None


# ── _build_io_params ──────────────────────────────────────────────────────────

class TestBuildIOParams:
    def _p(self, **kwargs) -> IOQueryParams:
        return IOQueryParams(year=2025, **kwargs)

    def test_fa_role_cost_owner_none(self):
        result = _build_io_params(self._p(), role="fa")
        assert result["cost_owner"] is None

    def test_non_fa_role_sets_cost_owner(self):
        result = _build_io_params(self._p(), role="sci")
        assert result["cost_owner"] == "SCI"

    def test_division_role_sets_ea_cost_center(self):
        result = _build_io_params(self._p(), role="hld")
        assert result["ea_cost_center"] == "HLD"

    def test_explicit_cost_owner_param_used_as_is(self):
        result = _build_io_params(self._p(cost_owner="BBA"), role="fa")
        assert result["cost_owner"] == "BBA"

    def test_explicit_cost_owner_overrides_role_for_non_fa(self):
        result = _build_io_params(self._p(cost_owner="SPECIFIC"), role="sci")
        assert result["cost_owner"] == "SPECIFIC"

    def test_cost_center_like_built(self):
        result = _build_io_params(self._p(cost_center="IT"), role="fa")
        assert result["cost_center_like"] == "%IT%"

    def test_q_like_built(self):
        result = _build_io_params(self._p(q="project"), role="fa")
        assert result["q_like"] == "%project%"

    def test_year_passed_through(self):
        result = _build_io_params(self._p(pa_year=2024), role="fa")
        assert result["year"] == 2025
        assert result["pa_year"] == 2024


# ── _run_query ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
class TestRunQuery:
    def _make_mock_db(self, payload):
        mock_cur = AsyncMock()
        mock_cur.execute = AsyncMock()
        mock_cur.fetchone = AsyncMock(return_value=(payload,))
        mock_cur.__aenter__ = AsyncMock(return_value=mock_cur)
        mock_cur.__aexit__ = AsyncMock(return_value=False)

        mock_conn = MagicMock()
        mock_conn.cursor = MagicMock(return_value=mock_cur)
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=False)
        return mock_conn, mock_cur

    async def test_returns_dict_payload(self):
        payload = {"kpis": {"total": 100}}
        mock_conn, _ = self._make_mock_db(payload)
        with patch("app.services.finance_service.get_finance_db") as mock_gdb:
            mock_gdb.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_gdb.return_value.__aexit__ = AsyncMock(return_value=False)
            result = await _run_query("SELECT 1", {}, "test")
        assert result == payload

    async def test_parses_json_string_payload(self):
        payload = {"kpis": {"total": 50}}
        mock_conn, _ = self._make_mock_db(json.dumps(payload))
        with patch("app.services.finance_service.get_finance_db") as mock_gdb:
            mock_gdb.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_gdb.return_value.__aexit__ = AsyncMock(return_value=False)
            result = await _run_query("SELECT 1", {}, "test")
        assert result == payload

    async def test_returns_empty_dict_when_no_row(self):
        mock_conn, mock_cur = self._make_mock_db(None)
        mock_cur.fetchone = AsyncMock(return_value=None)
        with patch("app.services.finance_service.get_finance_db") as mock_gdb:
            mock_gdb.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_gdb.return_value.__aexit__ = AsyncMock(return_value=False)
            result = await _run_query("SELECT 1", {}, "test")
        assert result == {}


# ── get_dashboard ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
class TestGetDashboard:
    _cached = {"kpis": {"total": 999}, "table_by_gl": []}
    _params = FinanceQueryParams(year=2025)

    async def test_returns_cached_result_on_hit(self):
        with patch("app.services.finance_service.get_cached", AsyncMock(return_value=self._cached)), \
             patch("app.services.finance_service.set_cached", AsyncMock()) as mock_set:
            result = await get_dashboard("fa", self._params)
        assert result == self._cached
        mock_set.assert_not_called()

    async def test_queries_db_on_cache_miss(self):
        db_data = {"kpis": {"total": 42}}
        with patch("app.services.finance_service.get_cached", AsyncMock(return_value=None)), \
             patch("app.services.finance_service._run_query", AsyncMock(return_value=db_data)) as mock_rq, \
             patch("app.services.finance_service.set_cached", AsyncMock()):
            result = await get_dashboard("fa", self._params)
        assert result == db_data
        mock_rq.assert_called_once()

    async def test_stores_result_in_cache_on_miss(self):
        db_data = {"kpis": {"total": 42}}
        with patch("app.services.finance_service.get_cached", AsyncMock(return_value=None)), \
             patch("app.services.finance_service._run_query", AsyncMock(return_value=db_data)), \
             patch("app.services.finance_service.set_cached", AsyncMock()) as mock_set:
            await get_dashboard("fa", self._params)
        mock_set.assert_called_once()
        args = mock_set.call_args[0]
        assert args[1] == db_data

    async def test_propagates_db_exception(self):
        with patch("app.services.finance_service.get_cached", AsyncMock(return_value=None)), \
             patch("app.services.finance_service._run_query", AsyncMock(side_effect=RuntimeError("db error"))), \
             patch("app.services.finance_service.set_cached", AsyncMock()):
            with pytest.raises(RuntimeError, match="db error"):
                await get_dashboard("fa", self._params)

    async def test_cache_key_includes_role_and_prefix(self):
        captured_keys = []

        async def mock_get_cached(key):
            captured_keys.append(key)
            return None

        with patch("app.services.finance_service.get_cached", mock_get_cached), \
             patch("app.services.finance_service._run_query", AsyncMock(return_value={})), \
             patch("app.services.finance_service.set_cached", AsyncMock()):
            await get_dashboard("fa", self._params, cache_prefix="budget")

        assert "budget" in captured_keys[0]
        assert "fa" in captured_keys[0]


# ── get_io ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
class TestGetIO:
    _cached = {"kpis": {"total": 500}, "spending_by_dept": []}
    _params = IOQueryParams(year=2025)

    async def test_returns_cached_result_on_hit(self):
        with patch("app.services.finance_service.get_cached", AsyncMock(return_value=self._cached)), \
             patch("app.services.finance_service.set_cached", AsyncMock()) as mock_set:
            result = await get_io("fa", self._params)
        assert result == self._cached
        mock_set.assert_not_called()

    async def test_queries_db_on_cache_miss(self):
        db_data = {"kpis": {"total": 77}}
        with patch("app.services.finance_service.get_cached", AsyncMock(return_value=None)), \
             patch("app.services.finance_service._run_query", AsyncMock(return_value=db_data)) as mock_rq, \
             patch("app.services.finance_service.set_cached", AsyncMock()):
            result = await get_io("fa", self._params)
        assert result == db_data
        mock_rq.assert_called_once()

    async def test_stores_result_in_cache_on_miss(self):
        db_data = {"kpis": {"total": 77}}
        with patch("app.services.finance_service.get_cached", AsyncMock(return_value=None)), \
             patch("app.services.finance_service._run_query", AsyncMock(return_value=db_data)), \
             patch("app.services.finance_service.set_cached", AsyncMock()) as mock_set:
            await get_io("fa", self._params)
        mock_set.assert_called_once()

    async def test_propagates_db_exception(self):
        with patch("app.services.finance_service.get_cached", AsyncMock(return_value=None)), \
             patch("app.services.finance_service._run_query", AsyncMock(side_effect=RuntimeError("io error"))), \
             patch("app.services.finance_service.set_cached", AsyncMock()):
            with pytest.raises(RuntimeError, match="io error"):
                await get_io("fa", self._params)
