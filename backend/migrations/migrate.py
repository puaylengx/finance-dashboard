#!/usr/bin/env python3
"""Run or rollback SQL migrations against the configured database.

Usage:
    python migrate.py              # apply all pending migrations
    python migrate.py --rollback   # rollback all applied migrations in reverse order
"""
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


def _extract_down_sql(sql_text):
    """Parse -- DOWN: comment block and return a list of SQL statements."""
    lines = sql_text.splitlines()
    down_lines = []
    in_down = False

    for line in lines:
        stripped = line.strip()
        if stripped.upper().startswith("-- DOWN:"):
            in_down = True
            inline = stripped[len("-- DOWN:"):].strip()
            if inline:
                down_lines.append(inline)
        elif in_down and stripped.startswith("--"):
            content = stripped.lstrip("-").strip()
            if content:
                down_lines.append(content)
        elif in_down:
            break

    if not down_lines:
        return []

    _SQL_KEYWORDS = ("DROP", "DELETE", "ALTER", "TRUNCATE", "UPDATE", "INSERT", "CREATE")
    full_text = " ".join(down_lines)
    return [
        s.strip() for s in full_text.split(";")
        if s.strip() and s.strip().upper().startswith(_SQL_KEYWORDS)
    ]


def run_migrations():
    conn, tunnel = _get_connection()
    try:
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


def rollback_migrations():
    conn, tunnel = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute(f"""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_name = '{MIGRATIONS_TABLE}'
            )
        """)
        exists = cur.fetchone()[0]
        cur.close()

        if not exists:
            print("No migrations table found — nothing to rollback.")
            return

        sql_files = sorted(MIGRATIONS_DIR.glob("*.sql"), reverse=True)
        rolled_back = 0

        for sql_file in sql_files:
            cur = conn.cursor()
            cur.execute(
                f"SELECT 1 FROM {MIGRATIONS_TABLE} WHERE filename = %s",
                (sql_file.name,),
            )
            is_applied = cur.fetchone() is not None
            cur.close()

            if not is_applied:
                print(f"  SKIP  {sql_file.name} (not applied)")
                continue

            statements = _extract_down_sql(sql_file.read_text(encoding="utf-8"))
            if not statements:
                print(f"  WARN  {sql_file.name} — no -- DOWN: block found, skipping")
                continue

            print(f"  DOWN  {sql_file.name} ...", end=" ", flush=True)
            try:
                cur = conn.cursor()
                for stmt in statements:
                    cur.execute(stmt)
                cur.execute(
                    f"DELETE FROM {MIGRATIONS_TABLE} WHERE filename = %s",
                    (sql_file.name,),
                )
                cur.close()
                conn.commit()
                print("OK")
                rolled_back += 1
            except Exception as exc:
                conn.rollback()
                print(f"FAILED\n  Error: {exc}")
                sys.exit(1)

        print(f"\nDone — {rolled_back} migration(s) rolled back.")

    finally:
        conn.close()
        if tunnel:
            tunnel.stop()


if __name__ == "__main__":
    if "--rollback" in sys.argv:
        rollback_migrations()
    else:
        run_migrations()
