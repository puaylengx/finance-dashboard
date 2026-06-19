"""
ETL: Import ERP transactions from CSV → PostgreSQL erp_transactions table.

Usage:
    python etl/import_erp.py --file export_2025.csv --year 2025
    python etl/import_erp.py --file export_2025.csv --year 2025 --dry-run

Process:
    1. Read CSV (ERP export — utf-8-sig to handle Excel BOM)
    2. Validate each row with Pydantic (collect errors, don't abort on first bad row)
    3. Delete existing rows for the fiscal_year (idempotent — safe to re-run)
    4. Bulk insert all valid rows
    5. Print summary: rows read / valid / rejected

Column mapping:
    CSV header names are lowercased and stripped before mapping.
    Adjust _CSV_MAP below if ERP export uses different column names.
"""
import argparse
import csv
import logging
import os
import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from dotenv import load_dotenv
from pydantic import ValidationError

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent.parent))

from etl.schemas import ErpTransactionRow

logger = logging.getLogger("etl.import")

# ── Column name mapping: CSV header → schema field ────────────────────────────
# Adjust left-hand side to match actual ERP CSV export column names.
_CSV_MAP: dict[str, str] = {
    "fiscal_year":        "fiscal_year",
    "fiscal_month":       "fiscal_month",
    "trimester":          "trimester",
    "day":                "day",
    "month":              "month",
    "year":               "year",
    "doc_no":             "doc_no",
    "doc_date":           "doc_date",
    "funds_ctr":          "funds_ctr",
    "cost_ctr_id":        "cost_ctr_id",
    "cost_owner":         "cost_owner",
    "cost_note":          "cost_note",
    "io_goods":           "io_goods",
    "io_work":            "io_work",
    "io_activity":        "io_activity",
    "io_project":         "io_project",
    "order_description":  "order_description",
    "hr_ot":              "hr_ot",
    "gl_id":              "gl_id",
    "gl_description":     "gl_description",
    "amount":             "amount",
    "details":            "details",
    "mu_strategy":        "mu_strategy",
    "ic_strategy":        "ic_strategy",
}

_INT_FIELDS = {"fiscal_year", "fiscal_month", "trimester", "day", "month", "year", "doc_no"}
_DECIMAL_FIELDS = {"amount", "mu_strategy", "ic_strategy"}
_NULLABLE = {
    "cost_owner", "cost_note", "io_goods", "io_work", "io_activity",
    "io_project", "order_description", "hr_ot", "mu_strategy", "ic_strategy",
}


def _coerce(field: str, raw: str) -> int | Decimal | str | None:
    val = raw.strip() if raw else ""
    if not val and field in _NULLABLE:
        return None
    if field in _INT_FIELDS:
        return int(val)
    if field in _DECIMAL_FIELDS:
        try:
            return Decimal(val.replace(",", ""))
        except InvalidOperation:
            return None
    return val or None if field in _NULLABLE else val


def load_csv(filepath: str) -> list[dict]:
    with open(filepath, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return [{k.strip().lower(): v for k, v in row.items()} for row in reader]


def validate_rows(raw_rows: list[dict]) -> tuple[list[ErpTransactionRow], list[dict]]:
    valid: list[ErpTransactionRow] = []
    errors: list[dict] = []

    for i, row in enumerate(raw_rows, start=2):  # row 1 = header
        mapped = {}
        try:
            for csv_col, field in _CSV_MAP.items():
                mapped[field] = _coerce(field, row.get(csv_col, ""))
            valid.append(ErpTransactionRow.model_validate(mapped))
        except (ValidationError, ValueError, KeyError) as exc:
            errors.append({"row": i, "error": str(exc)})

    return valid, errors


def _get_connection():
    import psycopg

    mode = os.getenv("DB_MODE", "direct").lower()
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", 5432))
    db_name = os.getenv("DB_NAME", "ic_finance")
    db_user = os.getenv("DB_USER", "postgres")
    db_pass = os.getenv("DB_PASSWORD", "")

    tunnel = None
    if mode == "ssh":
        from sshtunnel import SSHTunnelForwarder

        kw: dict = dict(
            ssh_address_or_host=(os.environ["SSH_HOST"], int(os.getenv("SSH_PORT", 22))),
            ssh_username=os.environ["SSH_USERNAME"],
            remote_bind_address=(db_host, db_port),
            local_bind_address=("127.0.0.1", 0),
        )
        key = os.getenv("SSH_KEY_PATH")
        kw["ssh_pkey" if key else "ssh_password"] = key or os.getenv("SSH_PASSWORD")
        tunnel = SSHTunnelForwarder(**kw)
        tunnel.start()
        db_host, db_port = "127.0.0.1", tunnel.local_bind_port
        logger.info("SSH tunnel open on local port %d", db_port)

    conn = psycopg.connect(
        host=db_host, port=db_port, dbname=db_name,
        user=db_user, password=db_pass,
        options="-c timezone=UTC",
    )
    return conn, tunnel


_INSERT_SQL = """
INSERT INTO erp_transactions (
    fiscal_year, fiscal_month, trimester, day, month, year,
    doc_no, doc_date, funds_ctr, cost_ctr_id, cost_owner,
    cost_note, io_goods, io_work, io_activity, io_project,
    order_description, hr_ot, gl_id, gl_description, amount,
    details, mu_strategy, ic_strategy, created_at
) VALUES (
    %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s,
    %s, %s, %s, NOW()
)
"""


def load_to_db(rows: list[ErpTransactionRow], fiscal_year: int, dry_run: bool) -> int:
    conn, tunnel = _get_connection()
    try:
        with conn.cursor() as cur:
            (existing,) = cur.execute(
                "SELECT COUNT(*) FROM erp_transactions WHERE fiscal_year = %s", (fiscal_year,)
            ).fetchone()
            logger.info("Existing rows for %s: %d", fiscal_year, existing)

            if dry_run:
                logger.info("[DRY-RUN] Would delete %d rows and insert %d rows", existing, len(rows))
                return len(rows)

            cur.execute(
                "DELETE FROM erp_transactions WHERE fiscal_year = %s", (fiscal_year,)
            )
            logger.info("Deleted %d existing rows", existing)

            data = [
                (
                    r.fiscal_year, r.fiscal_month, r.trimester, r.day, r.month, r.year,
                    r.doc_no, r.doc_date, r.funds_ctr, r.cost_ctr_id, r.cost_owner,
                    r.cost_note, r.io_goods, r.io_work, r.io_activity, r.io_project,
                    r.order_description, r.hr_ot, r.gl_id, r.gl_description, r.amount,
                    r.details, r.mu_strategy, r.ic_strategy,
                )
                for r in rows
            ]
            cur.executemany(_INSERT_SQL, data)

        conn.commit()
        logger.info("Inserted %d rows", len(rows))
        return len(rows)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
        if tunnel:
            tunnel.stop()


def run(filepath: str, fiscal_year: int, dry_run: bool = False) -> None:
    started = datetime.now()
    print(f"{'[DRY-RUN] ' if dry_run else ''}ETL Start: {started:%Y-%m-%d %H:%M:%S}")
    print(f"File: {filepath}  |  Fiscal Year: {fiscal_year}")
    print("-" * 60)

    raw = load_csv(filepath)
    print(f"Rows read:     {len(raw)}")

    valid, errors = validate_rows(raw)
    print(f"Valid rows:    {len(valid)}")
    print(f"Rejected rows: {len(errors)}")

    if errors:
        print("\nFirst 10 rejected rows:")
        for e in errors[:10]:
            print(f"  Row {e['row']}: {e['error']}")

    if not valid:
        print("\nNo valid rows — aborting.")
        sys.exit(1)

    inserted = load_to_db(valid, fiscal_year, dry_run=dry_run)

    elapsed = (datetime.now() - started).total_seconds()
    print(f"\n{'[DRY-RUN] ' if dry_run else ''}Done: {inserted} rows loaded in {elapsed:.1f}s")
    if errors:
        print(f"WARNING: {len(errors)} rows rejected — review errors above")
        sys.exit(0)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Import ERP transactions from CSV to PostgreSQL")
    parser.add_argument("--file", required=True, help="Path to ERP CSV export file")
    parser.add_argument("--year", required=True, type=int, help="Fiscal year to import (existing rows will be replaced)")
    parser.add_argument("--dry-run", action="store_true", help="Validate only — do not write to DB")
    args = parser.parse_args()
    run(args.file, args.year, dry_run=args.dry_run)
