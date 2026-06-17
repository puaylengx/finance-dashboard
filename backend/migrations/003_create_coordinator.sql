-- migration: 003_create_coordinator
-- DOWN: DROP TABLE IF EXISTS finance_coordinator CASCADE;
--       (CASCADE ลบ idx_finance_coordinator_username และ idx_finance_coordinator_active อัตโนมัติ)

CREATE TABLE IF NOT EXISTS finance_coordinator (
  id         SERIAL      PRIMARY KEY,
  username   TEXT        NOT NULL UNIQUE,
  active     BOOLEAN     NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ,
  updated_by TEXT,
  created_by TEXT
);

CREATE INDEX IF NOT EXISTS idx_finance_coordinator_username
  ON finance_coordinator (username);

CREATE INDEX IF NOT EXISTS idx_finance_coordinator_active
  ON finance_coordinator (active) WHERE active = TRUE;
