-- migration: 006_create_audit_log
-- Immutable audit trail for every authenticated API request on financial data
-- DOWN: DROP TABLE IF EXISTS audit_log;

CREATE TABLE IF NOT EXISTS audit_log (
    id          BIGSERIAL    PRIMARY KEY,
    user_id     TEXT         NOT NULL,
    action      TEXT         NOT NULL,
    resource    TEXT,
    ip_address  INET,
    status_code SMALLINT,
    timestamp   TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_audit_log_user_id   ON audit_log (user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log (timestamp DESC);

-- Production: run this against your app DB user to enforce append-only
-- REVOKE UPDATE, DELETE ON audit_log FROM <app_db_user>;
