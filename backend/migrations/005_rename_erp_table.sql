-- migration: 005_rename_erp_table
-- Rename erp_2025 → erp_transactions to support multi-year data via fiscal_year column
-- DOWN: ALTER TABLE erp_transactions RENAME TO erp_2025;

ALTER TABLE erp_2025 RENAME TO erp_transactions;
