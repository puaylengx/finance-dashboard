from datetime import datetime
from zoneinfo import ZoneInfo

from app.core.cache import invalidate_coordinator_cache
from app.core.database import get_admin_db
from app.core.logging import get_logger


class ConcurrentModificationError(Exception):
    """Raised when updated_at check fails — another request modified the record first."""

logger = get_logger(__name__)
_TZ_THAI = ZoneInfo("Asia/Bangkok")


def _now_thai() -> datetime:
    return datetime.now(tz=_TZ_THAI)


def _row_to_dict(description, row: tuple) -> dict:
    cols = [col.name for col in description]
    r = dict(zip(cols, row))
    for key in ("created_at", "updated_at"):
        if r.get(key) and hasattr(r[key], "astimezone"):
            r[key] = r[key].astimezone(_TZ_THAI)
    return r


async def list_coordinators(
    q: str | None = None,
    active: bool | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    conditions: list[str] = []
    sql_params: dict = {}

    if q:
        conditions.append("username ILIKE %(q)s")
        sql_params["q"] = f"%{q}%"
    if active is not None:
        conditions.append("active = %(active)s")
        sql_params["active"] = active

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    offset = (page - 1) * page_size

    async with get_admin_db() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"SELECT COUNT(*) FROM finance_coordinator {where}", sql_params
            )
            total: int = (await cur.fetchone())[0]

            sql_params["limit"] = page_size
            sql_params["offset"] = offset
            await cur.execute(
                f"""
                SELECT id, username, active, created_at, updated_at, created_by, updated_by
                FROM finance_coordinator
                {where}
                ORDER BY active DESC, created_at DESC
                LIMIT %(limit)s OFFSET %(offset)s
                """,
                sql_params,
            )
            rows = await cur.fetchall()
            items = [_row_to_dict(cur.description, r) for r in rows]

    total_pages = (total + page_size - 1) // page_size
    return {
        "success": True,
        "data": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
    }


async def add_coordinator(username: str, created_by: str) -> dict:
    now = _now_thai()
    async with get_admin_db() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                INSERT INTO finance_coordinator (username, created_by, created_at)
                VALUES (%(username)s, %(created_by)s, %(now)s)
                ON CONFLICT (username) DO UPDATE
                    SET active     = TRUE,
                        updated_at = EXCLUDED.created_at,
                        updated_by = EXCLUDED.created_by,
                        created_by = EXCLUDED.created_by
                RETURNING id, username, active, created_at, updated_at, created_by, updated_by
            """, {"username": username, "created_by": created_by, "now": now})
            row = await cur.fetchone()
            result = _row_to_dict(cur.description, row)
        await conn.commit()

    await invalidate_coordinator_cache(username)
    logger.info("Coordinator added/reactivated: %s by %s", username, created_by)
    return result


async def toggle_coordinator(
    coord_id: int,
    updated_by: str,
    expected_updated_at: datetime | None = None,
) -> dict | None:
    now = _now_thai()
    async with get_admin_db() as conn:
        async with conn.cursor() as cur:
            # Pessimistic lock: prevents concurrent toggle race condition
            await cur.execute(
                "SELECT id, updated_at FROM finance_coordinator WHERE id = %(id)s FOR UPDATE",
                {"id": coord_id},
            )
            current = await cur.fetchone()
            if not current:
                return None

            # Optimistic lock check: reject if client's version is stale
            if expected_updated_at is not None:
                db_updated_at = current[1]
                if db_updated_at != expected_updated_at:
                    raise ConcurrentModificationError(coord_id)

            await cur.execute(
                """
                UPDATE finance_coordinator
                   SET active     = NOT active,
                       updated_at = %(now)s,
                       updated_by = %(updated_by)s
                 WHERE id = %(id)s
                RETURNING id, username, active, created_at, updated_at, created_by, updated_by
                """,
                {"now": now, "updated_by": updated_by, "id": coord_id},
            )
            row = await cur.fetchone()
            result = _row_to_dict(cur.description, row)
        await conn.commit()

    await invalidate_coordinator_cache(result["username"])
    logger.info("Coordinator toggled: id=%s active=%s", coord_id, result["active"])
    return result
