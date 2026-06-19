"""
Reconciliation: Compare dashboard DB totals vs expected ERP totals.

Usage:
    # ระบุ expected total ตรง
    python etl/reconcile.py --year 2025 --expected-total 850000000.00

    # อ่านจาก CSV summary ที่ export จาก ERP
    python etl/reconcile.py --year 2025 --expected-file erp_summary_2025.csv

Exits with code 1 if absolute difference > tolerance (default 0.01% of expected).

Expected CSV format (erp_summary_2025.csv):
    fiscal_year,total_amount
    2025,850000000.00
"""
import argparse
import csv
import os
import sys
from decimal import Decimal
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent.parent))

_TOLERANCE_PCT = Decimal("0.01")  # 0.01%


def _get_db_total(fiscal_year: int) -> dict[str, Decimal]:
    """Return aggregate totals from DB for fiscal_year."""
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

    try:
        with psycopg.connect(
            host=db_host, port=db_port, dbname=db_name,
            user=db_user, password=db_pass,
        ) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT
                         COALESCE(SUM(amount), 0)  AS total_amount,
                         COUNT(*)                  AS row_count
                       FROM erp_transactions
                       WHERE fiscal_year = %s""",
                    (fiscal_year,),
                )
                total, count = cur.fetchone()
                return {"total_amount": Decimal(str(total)), "row_count": count}
    finally:
        if tunnel:
            tunnel.stop()


def _load_expected_from_csv(filepath: str, fiscal_year: int) -> Decimal:
    with open(filepath, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if int(row["fiscal_year"]) == fiscal_year:
                return Decimal(row["total_amount"].replace(",", "").strip())
    raise ValueError(f"fiscal_year {fiscal_year} not found in {filepath}")


def reconcile(fiscal_year: int, expected_total: Decimal) -> bool:
    db = _get_db_total(fiscal_year)
    actual = db["total_amount"]
    diff = abs(actual - expected_total)
    tolerance = expected_total * _TOLERANCE_PCT / 100

    width = 50
    print("=" * width)
    print(f"  Reconciliation Report — Fiscal Year {fiscal_year}")
    print("=" * width)
    print(f"  ERP expected total : {expected_total:>20,.2f}")
    print(f"  Dashboard DB total : {actual:>20,.2f}")
    print(f"  Difference         : {diff:>20,.2f}")
    print(f"  Tolerance (0.01%)  : {tolerance:>20,.2f}")
    print(f"  Row count in DB    : {db['row_count']:>20,}")
    print("-" * width)

    passed = diff <= tolerance
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"  Result: {status}")
    print("=" * width)
    return passed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reconcile dashboard totals vs ERP")
    parser.add_argument("--year", required=True, type=int)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--expected-total", type=Decimal, help="Expected total from ERP report")
    group.add_argument("--expected-file", help="CSV file with fiscal_year,total_amount columns")
    args = parser.parse_args()

    if args.expected_file:
        expected = _load_expected_from_csv(args.expected_file, args.year)
    else:
        expected = args.expected_total

    passed = reconcile(args.year, expected)
    sys.exit(0 if passed else 1)
