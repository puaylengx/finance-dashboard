-- migration: 007_enable_pg_stat_statements
-- Enable pg_stat_statements extension for automatic slow-query tracking
-- Requires superuser privilege — run with admin/superuser role
-- DOWN: DROP EXTENSION IF EXISTS pg_stat_statements;

-- Enable extension (idempotent)
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- After enabling, add to postgresql.conf (restart required):
--   shared_preload_libraries = 'pg_stat_statements'
--   pg_stat_statements.max = 1000
--   pg_stat_statements.track = all
--   log_min_duration_statement = 200   -- log queries slower than 200 ms

-- Usage: query top slow statements
-- SELECT query, calls, mean_exec_time, total_exec_time
-- FROM pg_stat_statements
-- ORDER BY mean_exec_time DESC
-- LIMIT 10;
