"""
DB Query Performance Tests
--------------------------
Requires a real database connection with production-size data.
Skipped by default — enable with: PERFORMANCE_TEST=1 pytest tests/performance/

These tests verify:
  1. Key queries complete within acceptable time thresholds
  2. EXPLAIN output shows Index Scan (not Seq Scan) on large tables
  3. pg_stat_statements is enabled and tracking queries
"""
import os
import time

import pytest

pytestmark = pytest.mark.performance

SKIP_REASON = "Set PERFORMANCE_TEST=1 to run DB performance tests against real database"
requires_perf_env = pytest.mark.skipif(
    not os.environ.get("PERFORMANCE_TEST"),
    reason=SKIP_REASON,
)

# Thresholds (milliseconds) — adjust after establishing baseline with real data
_THRESHOLD_DASHBOARD_MS = 3_000   # fiscal_year filter + CTE aggregation
_THRESHOLD_INDEX_SCAN_MS = 500    # simple index scan (no CTE)
_THRESHOLD_IO_MS = 3_000          # IO query with io_goods/project/work joins


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
async def finance_conn():
    """Real async DB connection — skips if DB unreachable."""
    from app.core.database import get_finance_db

    try:
        async with get_finance_db() as conn:
            yield conn
    except Exception as exc:
        pytest.skip(f"Finance DB not reachable: {exc}")


@pytest.fixture
async def admin_conn():
    """Real async DB connection to admin DB."""
    from app.core.database import get_admin_db

    try:
        async with get_admin_db() as conn:
            yield conn
    except Exception as exc:
        pytest.skip(f"Admin DB not reachable: {exc}")


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _explain(conn, sql: str, params: dict) -> str:
    """Return EXPLAIN (ANALYZE, FORMAT TEXT) output as a single string."""
    async with conn.cursor() as cur:
        await cur.execute(f"EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) {sql}", params)
        rows = await cur.fetchall()
    return "\n".join(r[0] for r in rows)


async def _timed(conn, sql: str, params: dict) -> float:
    """Execute a query and return wall-clock time in milliseconds."""
    async with conn.cursor() as cur:
        t0 = time.perf_counter()
        await cur.execute(sql, params)
        await cur.fetchone()
        return (time.perf_counter() - t0) * 1_000


# ── Index usage tests ─────────────────────────────────────────────────────────

@requires_perf_env
class TestIndexUsage:
    """Verify PostgreSQL uses indexes (not Seq Scan) on key filters."""

    async def test_fiscal_year_uses_index(self, finance_conn):
        plan = await _explain(
            finance_conn,
            "SELECT COUNT(*) FROM erp_transactions WHERE fiscal_year = %(y)s",
            {"y": 2025},
        )
        assert "Seq Scan" not in plan, (
            f"Expected Index Scan on idx_erp_fiscal_year, got Seq Scan.\n{plan}"
        )

    async def test_fiscal_year_month_uses_composite_index(self, finance_conn):
        plan = await _explain(
            finance_conn,
            """SELECT COUNT(*) FROM erp_transactions
               WHERE fiscal_year = %(y)s AND fiscal_month BETWEEN %(m1)s AND %(m2)s""",
            {"y": 2025, "m1": 1, "m2": 6},
        )
        # Accept either Index Scan or Bitmap Index Scan — both use idx_erp_fiscal_year_month
        assert "idx_erp_fiscal_year_month" in plan or "Index" in plan, (
            f"Expected composite index scan.\n{plan}"
        )

    async def test_cost_ctr_id_uses_index(self, finance_conn):
        plan = await _explain(
            finance_conn,
            """SELECT COUNT(*) FROM erp_transactions
               WHERE fiscal_year = %(y)s AND cost_ctr_id = %(cc)s""",
            {"y": 2025, "cc": "CC001"},
        )
        assert "Seq Scan" not in plan, (
            f"Expected Index Scan on idx_erp_cost_ctr_id.\n{plan}"
        )

    async def test_io_goods_partial_index(self, finance_conn):
        plan = await _explain(
            finance_conn,
            """SELECT COUNT(*) FROM erp_transactions
               WHERE fiscal_year = %(y)s AND io_goods IS NOT NULL""",
            {"y": 2025},
        )
        assert "idx_erp_io_goods" in plan or "Index" in plan, (
            f"Expected partial index scan on io_goods.\n{plan}"
        )


# ── Query execution time tests ────────────────────────────────────────────────

@requires_perf_env
class TestQueryExecutionTime:
    """Assert queries complete within acceptable thresholds with real data."""

    async def test_fiscal_year_count_under_threshold(self, finance_conn):
        elapsed = await _timed(
            finance_conn,
            "SELECT COUNT(*) FROM erp_transactions WHERE fiscal_year = %(y)s",
            {"y": 2025},
        )
        assert elapsed < _THRESHOLD_INDEX_SCAN_MS, (
            f"Simple index scan took {elapsed:.0f}ms > {_THRESHOLD_INDEX_SCAN_MS}ms threshold"
        )

    async def test_dashboard_cte_under_threshold(self, finance_conn):
        sql = """
        WITH base AS (
          SELECT erp.amount, erp.gl_id, erp.fiscal_month
          FROM erp_transactions erp
            LEFT JOIN master_gl gl ON erp.gl_id = gl.gl_id
          WHERE erp.fiscal_year = %(y)s
        )
        SELECT JSONB_BUILD_OBJECT(
          'total', SUM(amount),
          'count', COUNT(*)
        ) FROM base
        """
        elapsed = await _timed(finance_conn, sql, {"y": 2025})
        assert elapsed < _THRESHOLD_DASHBOARD_MS, (
            f"Dashboard CTE took {elapsed:.0f}ms > {_THRESHOLD_DASHBOARD_MS}ms threshold"
        )


# ── pg_stat_statements availability ──────────────────────────────────────────

@requires_perf_env
class TestPgStatStatements:
    """Verify pg_stat_statements extension is installed and accessible."""

    async def test_extension_is_installed(self, finance_conn):
        async with finance_conn.cursor() as cur:
            await cur.execute(
                "SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements'"
            )
            row = await cur.fetchone()
        assert row is not None, (
            "pg_stat_statements extension not found. "
            "Run: migration 007_enable_pg_stat_statements.sql as superuser"
        )

    async def test_can_query_slow_statements(self, finance_conn):
        async with finance_conn.cursor() as cur:
            await cur.execute(
                "SELECT query, calls, mean_exec_time FROM pg_stat_statements LIMIT 1"
            )
            # No exception means extension is functional
