-- migration: 004_create_indexes
-- Performance indexes for erp_2025 query patterns
-- DOWN:
--   DROP INDEX IF EXISTS idx_erp_fiscal_year;
--   DROP INDEX IF EXISTS idx_erp_fiscal_year_month;
--   DROP INDEX IF EXISTS idx_erp_year_month;
--   DROP INDEX IF EXISTS idx_erp_gl_id;
--   DROP INDEX IF EXISTS idx_erp_cost_ctr_id;
--   DROP INDEX IF EXISTS idx_erp_cost_owner;
--   DROP INDEX IF EXISTS idx_erp_io_goods;
--   DROP INDEX IF EXISTS idx_erp_io_project;
--   DROP INDEX IF EXISTS idx_erp_io_work;
--   DROP INDEX IF EXISTS idx_master_cost_ctr_id;
--   DROP INDEX IF EXISTS idx_master_gl_id;
--   DROP INDEX IF EXISTS idx_master_io_goods_id;
--   DROP INDEX IF EXISTS idx_master_io_project_id;
--   DROP INDEX IF EXISTS idx_master_io_work_id;

-- Primary lookup: fiscal_year (used in every dashboard query)
CREATE INDEX IF NOT EXISTS idx_erp_fiscal_year
  ON erp_2025 (fiscal_year);

-- Composite: fiscal_year + fiscal_month (month-range filters)
CREATE INDEX IF NOT EXISTS idx_erp_fiscal_year_month
  ON erp_2025 (fiscal_year, fiscal_month);

-- Calendar year + month (pa_year queries)
CREATE INDEX IF NOT EXISTS idx_erp_year_month
  ON erp_2025 (year, month);

-- GL filters
CREATE INDEX IF NOT EXISTS idx_erp_gl_id
  ON erp_2025 (gl_id);

-- Cost center filters
CREATE INDEX IF NOT EXISTS idx_erp_cost_ctr_id
  ON erp_2025 (cost_ctr_id);

-- Cost owner filters
CREATE INDEX IF NOT EXISTS idx_erp_cost_owner
  ON erp_2025 (cost_owner);

-- IO order fields (used in IO dashboard queries)
CREATE INDEX IF NOT EXISTS idx_erp_io_goods
  ON erp_2025 (io_goods) WHERE io_goods IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_erp_io_project
  ON erp_2025 (io_project) WHERE io_project IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_erp_io_work
  ON erp_2025 (io_work) WHERE io_work IS NOT NULL;

-- Master tables: primary key indexes (text PKs need explicit indexing in some setups)
CREATE INDEX IF NOT EXISTS idx_master_cost_ctr_id
  ON master_cost_ctr (cost_center_id);

CREATE INDEX IF NOT EXISTS idx_master_gl_id
  ON master_gl (gl_id);

CREATE INDEX IF NOT EXISTS idx_master_io_goods_id
  ON master_io_goods (io_good_id);

CREATE INDEX IF NOT EXISTS idx_master_io_project_id
  ON master_io_project (io_project_id);

CREATE INDEX IF NOT EXISTS idx_master_io_work_id
  ON master_io_work (io_work_id);
