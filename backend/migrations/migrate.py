#!/usr/bin/env python3
"""Run all pending SQL migrations against the configured database."""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

MIGRATIONS_DIR   = Path(__file__).parent
MIGRATIONS_TABLE = "schema_migrations"


def _get_connection():
    import warnings
    from cryptography.utils import CryptographyDeprecationWarning
    warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)

    mode      = (os.getenv("DB_MODE", "direct") or "direct").lower()
    db_host   = os.getenv("DB_HOST", "localhost")
    db_port   = int(os.getenv("DB_PORT", 5432))
    db_name   = os.getenv("DB_NAME", "ic_finance")
    db_user   = os.getenv("DB_USER", "postgres")
    db_pass   = os.getenv("DB_PASSWORD", "")

    tunnel = None
    if mode == "ssh":
        from sshtunnel import SSHTunnelForwarder
        tunnel_kwargs = dict(
            ssh_address_or_host=(os.environ["SSH_HOST"], int(os.getenv("SSH_PORT", 22))),
            ssh_username=os.environ["SSH_USERNAME"],
            remote_bind_address=(db_host, db_port),
            local_bind_address=("127.0.0.1", 0),
        )
        key_path = os.getenv("SSH_KEY_PATH")
        if key_path:
            tunnel_kwargs["ssh_pkey"] = key_path
        else:
            tunnel_kwargs["ssh_password"] = os.getenv("SSH_PASSWORD")
        tunnel = SSHTunnelForwarder(**tunnel_kwargs)
        tunnel.start()
        db_host = "127.0.0.1"
        db_port = tunnel.local_bind_port
        print(f"[SSH] Tunnel open on local port {db_port}")

    import psycopg
    conn = psycopg.connect(
        host=db_host,
        port=db_port,
        dbname=db_name,
        user=db_user,
        password=db_pass,
        options="-c timezone=UTC",
        autocommit=False,
    )
    return conn, tunnel


def run_migrations():
    conn, tunnel = _get_connection()
    try:
        # สร้างตาราง tracking ถ้ายังไม่มี
        cur = conn.cursor()
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {MIGRATIONS_TABLE} (
                id         SERIAL PRIMARY KEY,
                filename   TEXT        NOT NULL UNIQUE,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)
        cur.close()
        conn.commit()

        sql_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
        applied   = 0

        for sql_file in sql_files:
            # ตรวจว่า migration นี้รันไปแล้วหรือยัง
            cur = conn.cursor()
            cur.execute(
                f"SELECT 1 FROM {MIGRATIONS_TABLE} WHERE filename = %s",
                (sql_file.name,),
            )
            already_applied = cur.fetchone() is not None
            cur.close()

            if already_applied:
                print(f"  SKIP  {sql_file.name}")
                continue

            # รัน migration
            print(f"  RUN   {sql_file.name} ...", end=" ", flush=True)
            sql = sql_file.read_text(encoding="utf-8")

            try:
                cur = conn.cursor()
                cur.execute(sql)
                cur.execute(
                    f"INSERT INTO {MIGRATIONS_TABLE} (filename) VALUES (%s)",
                    (sql_file.name,),
                )
                cur.close()
                conn.commit()
                print("OK")
                applied += 1
            except Exception as exc:
                conn.rollback()
                print(f"FAILED\n  Error: {exc}")
                sys.exit(1)

        print(f"\nDone — {applied} migration(s) applied.")

    finally:
        conn.close()
        if tunnel:
            tunnel.stop()


if __name__ == "__main__":
    run_migrations()
