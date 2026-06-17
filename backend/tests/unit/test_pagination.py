import pytest

from app.schemas.common import PaginationParams, PaginatedResponse
from app.schemas.finance import FinanceQueryParams, IOQueryParams
from app.services.finance_service import _apply_top_n, _FINANCE_TABLE_KEYS, _IO_TABLE_KEYS


class TestPaginationParams:
    def test_defaults(self):
        p = PaginationParams()
        assert p.page == 1
        assert p.page_size == 20

    def test_custom_values(self):
        p = PaginationParams(page=5, page_size=50)
        assert p.page == 5
        assert p.page_size == 50

    def test_page_must_be_at_least_1(self):
        with pytest.raises(Exception):
            PaginationParams(page=0)

    def test_page_size_max_is_100(self):
        with pytest.raises(Exception):
            PaginationParams(page_size=101)

    def test_page_size_min_is_1(self):
        with pytest.raises(Exception):
            PaginationParams(page_size=0)


class TestPaginatedResponse:
    def test_shape(self):
        r = PaginatedResponse[dict](
            data=[{"id": 1}, {"id": 2}],
            page=2,
            page_size=10,
            total=25,
            total_pages=3,
        )
        assert r.success is True
        assert len(r.data) == 2
        assert r.total == 25
        assert r.total_pages == 3

    def test_empty_data(self):
        r = PaginatedResponse[dict](
            data=[], page=1, page_size=20, total=0, total_pages=0
        )
        assert r.data == []
        assert r.total == 0


class TestFinanceTopNParam:
    def test_top_n_defaults_to_none(self):
        p = FinanceQueryParams(year=2025)
        assert p.top_n is None

    def test_top_n_valid_value(self):
        p = FinanceQueryParams(year=2025, top_n=10)
        assert p.top_n == 10

    def test_top_n_min_is_1(self):
        with pytest.raises(Exception):
            FinanceQueryParams(year=2025, top_n=0)

    def test_top_n_max_is_500(self):
        with pytest.raises(Exception):
            FinanceQueryParams(year=2025, top_n=501)

    def test_top_n_boundary_values(self):
        assert FinanceQueryParams(year=2025, top_n=1).top_n == 1
        assert FinanceQueryParams(year=2025, top_n=500).top_n == 500


class TestIOTopNParam:
    def test_top_n_defaults_to_none(self):
        p = IOQueryParams(year=2025)
        assert p.top_n is None

    def test_top_n_valid_value(self):
        p = IOQueryParams(year=2025, top_n=25)
        assert p.top_n == 25


class TestApplyTopN:
    def _make_finance_result(self, rows_per_table: int = 50) -> dict:
        rows = [{"gl_id": i, "total": i * 100} for i in range(rows_per_table)]
        return {
            "kpis": {"total_amount": 1_000_000},
            "trend_month": [{"month": "Jan", "total": 500}],
            "table_by_gl": list(rows),
            "table_by_cost_center": list(rows),
            "table_by_gl_division": list(rows),
            "table_by_cost_center_division": list(rows),
            "table_by_gl_all": list(rows),
            "table_by_cost_center_all": list(rows),
            "pivot_table_by_gl_detail": list(rows),
            "pivot_table_by_gl_detail_division": list(rows),
            "pivot_table_by_gl_detail_all": list(rows),
        }

    def test_no_op_when_top_n_is_none(self):
        result = self._make_finance_result(50)
        out = _apply_top_n(result, _FINANCE_TABLE_KEYS, top_n=None)
        assert len(out["table_by_gl"]) == 50

    def test_slices_all_table_keys(self):
        result = self._make_finance_result(50)
        out = _apply_top_n(result, _FINANCE_TABLE_KEYS, top_n=10)
        for key in _FINANCE_TABLE_KEYS:
            assert len(out[key]) == 10, f"Expected 10 rows in {key}"

    def test_does_not_touch_non_table_keys(self):
        result = self._make_finance_result(50)
        out = _apply_top_n(result, _FINANCE_TABLE_KEYS, top_n=5)
        assert out["kpis"] == {"total_amount": 1_000_000}
        assert len(out["trend_month"]) == 1

    def test_top_n_larger_than_array_returns_all(self):
        result = self._make_finance_result(5)
        out = _apply_top_n(result, _FINANCE_TABLE_KEYS, top_n=100)
        assert len(out["table_by_gl"]) == 5

    def test_top_n_one_returns_single_row(self):
        result = self._make_finance_result(30)
        out = _apply_top_n(result, _FINANCE_TABLE_KEYS, top_n=1)
        assert len(out["table_by_gl"]) == 1

    def test_missing_keys_are_ignored(self):
        result = {"kpis": {}, "table_by_gl": [{"id": i} for i in range(20)]}
        out = _apply_top_n(result, _FINANCE_TABLE_KEYS, top_n=5)
        assert len(out["table_by_gl"]) == 5
        assert "table_by_cost_center" not in out

    def test_io_table_keys_are_sliced(self):
        rows = [{"cost_center_description": f"CC{i}", "total": i} for i in range(30)]
        result = {
            "kpis": {},
            "spending_by_dept": list(rows),
            "spending_by_division": list(rows),
            "pivot_table_by_io_goods": list(rows),
            "pivot_table_by_io_project": list(rows),
            "pivot_table_by_io_work": list(rows),
        }
        out = _apply_top_n(result, _IO_TABLE_KEYS, top_n=8)
        for key in _IO_TABLE_KEYS:
            assert len(out[key]) == 8

    def test_non_dict_result_returned_as_is(self):
        assert _apply_top_n(None, _FINANCE_TABLE_KEYS, top_n=5) is None  # type: ignore
        assert _apply_top_n({}, _FINANCE_TABLE_KEYS, top_n=5) == {}
