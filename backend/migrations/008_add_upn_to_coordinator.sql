-- migration: 008_add_upn_to_coordinator
-- Add upn (User Principal Name) column for exact Entra preferred_username matching
-- DOWN: ALTER TABLE finance_coordinator DROP COLUMN IF EXISTS upn;
--       DROP INDEX IF EXISTS idx_finance_coordinator_upn;

ALTER TABLE finance_coordinator
  ADD COLUMN IF NOT EXISTS upn TEXT;

CREATE UNIQUE INDEX IF NOT EXISTS idx_finance_coordinator_upn
  ON finance_coordinator (LOWER(upn))
  WHERE upn IS NOT NULL;
