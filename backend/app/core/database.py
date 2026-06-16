import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator

import psycopg
import psycopg_pool
from psycopg import AsyncClientCursor
from sshtunnel import SSHTunnelForwarder

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_pool: psycopg_pool.AsyncConnectionPool | None = None
_tunnel: SSHTunnelForwarder | None = None


async def init_db() -> None:
    global _pool, _tunnel

    if settings.db_mode == "ssh":
        if not settings.ssh_host:
            raise ValueError("SSH_HOST is required when DB_MODE=ssh")

        tunnel_kwargs: dict = dict(
            ssh_address_or_host=(settings.ssh_host, settings.ssh_port),
            ssh_username=settings.ssh_username,
            remote_bind_address=(settings.db_host, settings.db_port),
            local_bind_address=("127.0.0.1", 0),
        )
        if settings.ssh_key_path:
            tunnel_kwargs["ssh_pkey"] = settings.ssh_key_path
        else:
            tunnel_kwargs["ssh_password"] = settings.ssh_password

        _tunnel = SSHTunnelForwarder(**tunnel_kwargs)
        await asyncio.to_thread(_tunnel.start)
        connect_host = "127.0.0.1"
        connect_port = _tunnel.local_bind_port
        logger.info("SSH tunnel started on local port %s", connect_port)
    else:
        connect_host = settings.db_host
        connect_port = settings.db_port

    conninfo = (
        f"host={connect_host} port={connect_port} "
        f"dbname={settings.db_name} user={settings.db_user} "
        f"password={settings.db_password} "
        f"connect_timeout={settings.db_connect_timeout} "
        f"options='-c timezone=UTC'"
    )

    # AsyncClientCursor keeps %(name)s syntax compatible with psycopg2-style SQL
    _pool = psycopg_pool.AsyncConnectionPool(
        conninfo=conninfo,
        min_size=settings.db_pool_min_size,
        max_size=settings.db_pool_max_size,
        open=False,
        kwargs={"cursor_factory": AsyncClientCursor},
    )
    await _pool.open()
    logger.info(
        "DB pool ready (mode=%s host=%s:%s pool=%d-%d)",
        settings.db_mode, connect_host, connect_port,
        settings.db_pool_min_size, settings.db_pool_max_size,
    )


async def close_db() -> None:
    global _pool, _tunnel
    if _pool:
        await _pool.close()
        _pool = None
        logger.info("DB pool closed")
    if _tunnel:
        await asyncio.to_thread(_tunnel.stop)
        _tunnel = None
        logger.info("SSH tunnel closed")


@asynccontextmanager
async def get_db() -> AsyncIterator[psycopg.AsyncConnection]:
    if _pool is None:
        raise RuntimeError("Database pool not initialized — call init_db() first")
    async with _pool.connection() as conn:
        yield conn
