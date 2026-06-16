from datetime import datetime
from zoneinfo import ZoneInfo

from app.core.database import get_db
from app.core.logging import get_logger
from app.services.cache_service import invalidate_coordinator_cache

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


async def list_coordinators() -> list[dict]:
    async with get_db() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                SELECT id, username, active, created_at, updated_at, created_by, updated_by
                FROM finance_coordinator
                ORDER BY active DESC, created_at DESC
            """)
            rows = await cur.fetchall()
            return [_row_to_dict(cur.description, r) for r in rows]


async def add_coordinator(username: str, created_by: str) -> dict:
    now = _now_thai()
    async with get_db() as conn:
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


async def toggle_coordinator(coord_id: int, updated_by: str) -> dict | None:
    now = _now_thai()
    async with get_db() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                UPDATE finance_coordinator
                   SET active     = NOT active,
                       updated_at = %(now)s,
                       updated_by = %(updated_by)s
                 WHERE id = %(id)s
                RETURNING id, username, active, created_at, updated_at, created_by, updated_by
            """, {"now": now, "updated_by": updated_by, "id": coord_id})
            row = await cur.fetchone()
            if not row:
                return None
            result = _row_to_dict(cur.description, row)
        await conn.commit()

    await invalidate_coordinator_cache(result["username"])
    logger.info("Coordinator toggled: id=%s active=%s", coord_id, result["active"])
    return result
