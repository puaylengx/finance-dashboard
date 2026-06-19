-- EXPLAIN ANALYZE scripts for Finance Dashboard
-- Run against real DB (with production-size data) to verify index usage
-- Usage: psql -d <database> -f explain_queries.sql
--
-- Expected results:
--   idx_erp_fiscal_year       → "Index Scan" on fiscal_year filter
--   idx_erp_fiscal_year_month → "Index Scan" on fiscal_year + fiscal_month
--   idx_erp_cost_ctr_id       → "Index Scan" on cost_ctr_id filter
--   Master tables             → "Index Scan" via master_*_id indexes
--
-- Red flag: "Seq Scan" on erp_transactions with rows > 10,000 means index is not used.
--   Fix: ANALYZE erp_transactions; (refresh statistics) or VACUUM ANALYZE;

-- ── 1. Dashboard query: fiscal_year filter (most common) ──────────────────────
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT COUNT(*)
FROM erp_transactions
WHERE fiscal_year = 2025;
-- Expected plan: "Index Scan using idx_erp_fiscal_year on erp_transactions"

-- ── 2. Dashboard query: fiscal_year + fiscal_month (month range) ──────────────
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT COUNT(*)
FROM erp_transactions
WHERE fiscal_year = 2025
  AND fiscal_month BETWEEN 1 AND 6;
-- Expected plan: "Index Scan using idx_erp_fiscal_year_month on erp_transactions"

-- ── 3. Cost center filter ─────────────────────────────────────────────────────
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT COUNT(*)
FROM erp_transactions
WHERE fiscal_year = 2025
  AND cost_ctr_id = 'CC001';
-- Expected plan: Bitmap Index Scan on idx_erp_cost_ctr_id

-- ── 4. Full dashboard CTE (realistic load — replace 2025 with actual year) ────
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
WITH base AS (
  SELECT erp.fiscal_year, erp.gl_id, erp.cost_ctr_id, erp.amount, erp.fiscal_month
  FROM erp_transactions erp
    LEFT JOIN master_gl       gl      ON erp.gl_id       = gl.gl_id
    LEFT JOIN master_cost_ctr costCtr ON erp.cost_ctr_id = costCtr.cost_center_id
  WHERE (erp.fiscal_year = 2025)
    AND (erp.fiscal_month >= 1)
    AND (erp.fiscal_month <= 12)
)
SELECT COALESCE(SUM(amount), 0) AS total FROM base;
-- Expected: index scans on erp_transactions, not Seq Scan
-- Hash Join on master tables is acceptable (small tables)

-- ── 5. IO query: io_goods partial index ───────────────────────────────────────
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT COUNT(*)
FROM erp_transactions
WHERE fiscal_year = 2025
  AND io_goods IS NOT NULL;
-- Expected: "Index Scan using idx_erp_io_goods" (partial index WHERE io_goods IS NOT NULL)

-- ── 6. pg_stat_statements: top 5 slowest (run after extension enabled) ────────
-- SELECT
--   LEFT(query, 80)  AS query_preview,
--   calls,
--   ROUND(mean_exec_time::numeric, 2) AS avg_ms,
--   ROUND(total_exec_time::numeric, 2) AS total_ms
-- FROM pg_stat_statements
-- ORDER BY mean_exec_time DESC
-- LIMIT 5;

-- ── 7. Index usage health check ───────────────────────────────────────────────
SELECT
  schemaname,
  tablename,
  indexname,
  idx_scan   AS times_used,
  idx_tup_read AS tuples_read
FROM pg_stat_user_indexes
WHERE tablename IN ('erp_transactions', 'master_gl', 'master_cost_ctr',
                    'master_io_goods', 'master_io_project', 'master_io_work')
ORDER BY tablename, idx_scan DESC;
-- Red flag: idx_scan = 0 after production traffic means index is never used → consider dropping
