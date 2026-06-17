from app.core.config import settings
from app.core.database import get_db
from app.core.logging import get_logger
from app.core.security import ILIKE_ROOT_OVERRIDE, is_division, is_fa
from app.schemas.finance import FinanceQueryParams, IOQueryParams
from app.services.cache_service import get_cached, set_cached

_FINANCE_TABLE_KEYS = (
    "table_by_gl", "table_by_cost_center",
    "table_by_gl_division", "table_by_cost_center_division",
    "table_by_gl_all", "table_by_cost_center_all",
    "pivot_table_by_gl_detail", "pivot_table_by_gl_detail_division", "pivot_table_by_gl_detail_all",
)

_IO_TABLE_KEYS = (
    "spending_by_dept", "spending_by_division",
    "pivot_table_by_io_goods", "pivot_table_by_io_project", "pivot_table_by_io_work",
)


def _apply_top_n(result: dict, keys: tuple, top_n: int | None) -> dict:
    if top_n is None or not isinstance(result, dict):
        return result
    for key in keys:
        arr = result.get(key)
        if isinstance(arr, list):
            result[key] = arr[:top_n]
    return result

logger = get_logger(__name__)

# ── SQL: Finance / Budget dashboard ──────────────────────────────────────────

_SQL_DASHBOARD = """
WITH base AS (
  SELECT
    erp.fiscal_year,
    erp.month AS month_number,
    CASE
      WHEN erp.month = 1  THEN 'January'   WHEN erp.month = 2  THEN 'February'
      WHEN erp.month = 3  THEN 'March'     WHEN erp.month = 4  THEN 'April'
      WHEN erp.month = 5  THEN 'May'       WHEN erp.month = 6  THEN 'June'
      WHEN erp.month = 7  THEN 'July'      WHEN erp.month = 8  THEN 'August'
      WHEN erp.month = 9  THEN 'September' WHEN erp.month = 10 THEN 'October'
      WHEN erp.month = 11 THEN 'November'  WHEN erp.month = 12 THEN 'December'
    END AS month,
    erp.gl_id,
    TRIM(erp.gl_description)                          AS gl_description,
    COALESCE(NULLIF(TRIM(erp.cost_owner),''),'Other') AS cost_owner,
    TRIM(costOwn.cost_center_eng)                     AS cost_own_eng,
    TRIM(costOwn.cost_center_description)             AS cost_own_description,
    TRIM(costCtr.cost_center_eng)                     AS cost_center_eng,
    TRIM(costCtr.cost_center_description)             AS cost_center_description,
    COALESCE(gl.group_id,'Other')                     AS gl_group,
    TRIM(gl.group_description)                        AS group_description,
    TRIM(COALESCE(erp.details,''))                    AS details,
    erp.amount,
    erp.fiscal_month,
    MOD(erp.month + 5, 12) + 1                                    AS pa_month,
    CASE WHEN erp.month >= 7 THEN erp.year ELSE erp.year - 1 END  AS pa_year
  FROM erp_2025 erp
    LEFT JOIN master_gl       gl      ON erp.gl_id       = gl.gl_id
    LEFT JOIN master_cost_ctr costCtr ON erp.cost_ctr_id = costCtr.cost_center_id
    LEFT JOIN master_cost_ctr costOwn ON erp.cost_owner  = costOwn.cost_center_id
  WHERE (
      (%(pa_year)s IS NULL     AND erp.fiscal_year = %(year)s)
      OR (%(pa_year)s IS NOT NULL AND CASE WHEN erp.month >= 7 THEN erp.year ELSE erp.year - 1 END = %(pa_year)s)
    )
    AND (%(month_from)s IS NULL OR CASE WHEN %(pa_year)s IS NULL THEN erp.fiscal_month ELSE MOD(erp.month + 5, 12) + 1 END >= %(month_from)s)
    AND (%(month_to)s   IS NULL OR CASE WHEN %(pa_year)s IS NULL THEN erp.fiscal_month ELSE MOD(erp.month + 5, 12) + 1 END <= %(month_to)s)
    AND (%(gl_group)s    IS NULL OR COALESCE(gl.group_id,'Other') = %(gl_group)s)
    AND (%(cost_center)s IS NULL OR costCtr.cost_center_description ILIKE %(cost_center_like)s)
    AND (%(cost_owner)s  IS NULL
         OR TRIM(erp.cost_owner) = %(cost_owner)s
         OR costOwn.cost_center_description ILIKE %(cost_owner_like)s
         OR (%(ea_cost_center)s IS NOT NULL
             AND costOwn.cost_center_description ILIKE 'EA'
             AND UPPER(TRIM(costCtr.cost_center_description)) = %(ea_cost_center)s))
    AND (%(q)s IS NULL
         OR erp.details        ILIKE %(q_like)s
         OR erp.gl_description ILIKE %(q_like)s)
)
SELECT JSONB_BUILD_OBJECT(
  'kpis', JSONB_BUILD_OBJECT(
    'total_amount',       (SELECT COALESCE(SUM(amount),0) FROM base),
    'total_budget',       900000000,
    'doc_count',          (SELECT COUNT(*) FROM base),
    'avg_amount_per_doc', (SELECT COALESCE(AVG(amount),0) FROM base)
  ),
  'trend_month', (
    SELECT JSONB_AGG(
      JSONB_BUILD_OBJECT('month',month,'month_number',month_number,'fiscal_month',fiscal_month,'pa_month',pa_month,'pa_year',pa_year,'total',total)
      ORDER BY month_number
    )
    FROM (
      SELECT month, month_number, fiscal_month, pa_month, pa_year, SUM(amount) AS total
      FROM base GROUP BY month, month_number, fiscal_month, pa_month, pa_year
    ) t
  ),
  'table_by_gl', (
    SELECT COALESCE(JSONB_AGG(
      JSONB_BUILD_OBJECT('gl_id',gl_id,'gl_description',gl_description,'gl_group',gl_group,'total',total)
      ORDER BY gl_group), '[]'::jsonb)
    FROM (
      SELECT gl_id, gl_description, cost_own_description, MAX(gl_group) AS gl_group, SUM(amount) AS total
      FROM base WHERE cost_center_description NOT IN ('BBA','HLD','SCI','SS','THM','FAA','MBA','MM')
      GROUP BY gl_id, gl_description, cost_own_description
    ) g
  ),
  'table_by_cost_center', (
    SELECT COALESCE(JSONB_AGG(
      JSONB_BUILD_OBJECT('cost_center_eng',cost_center_eng,'cost_center_description',cost_center_description,'total',total)
      ORDER BY total DESC), '[]'::jsonb)
    FROM (
      SELECT MAX(cost_center_eng) AS cost_center_eng, MAX(cost_center_description) AS cost_center_description, SUM(amount) AS total
      FROM base WHERE cost_center_description NOT IN ('BBA','HLD','SCI','SS','THM','FAA','MBA','MM')
      GROUP BY cost_center_description
    ) c
  ),
  'pivot_table_by_gl_detail', (
    SELECT COALESCE(JSONB_AGG(
      JSONB_BUILD_OBJECT('gl_id',gl_id,'gl_description',gl_description,'total_amount',total_amount,'details_breakdown',details_breakdown)
      ORDER BY gl_id), '[]'::jsonb)
    FROM (
      SELECT gl_id, MAX(gl_description) AS gl_description, SUM(detail_amount) AS total_amount,
        COALESCE(JSONB_AGG(JSONB_BUILD_OBJECT('details',details,'amount',detail_amount) ORDER BY detail_amount DESC),'[]'::jsonb) AS details_breakdown
      FROM (
        SELECT gl_id, gl_description, details, cost_own_description, SUM(amount) AS detail_amount
        FROM base WHERE cost_center_description NOT IN ('BBA','HLD','SCI','SS','THM','FAA','MBA','MM')
        GROUP BY gl_id, gl_description, details, cost_own_description
      ) d GROUP BY gl_id
    ) x
  ),
  'table_by_gl_division', (
    SELECT COALESCE(JSONB_AGG(
      JSONB_BUILD_OBJECT('gl_id',gl_id,'gl_description',gl_description,'gl_group',gl_group,'total',total)
      ORDER BY gl_group), '[]'::jsonb)
    FROM (
      SELECT gl_id, gl_description, cost_own_description, MAX(gl_group) AS gl_group, SUM(amount) AS total
      FROM base WHERE cost_center_description IN ('BBA','HLD','SCI','SS','THM','FAA','MBA','MM')
      GROUP BY gl_id, gl_description, cost_own_description
    ) g
  ),
  'table_by_cost_center_division', (
    SELECT COALESCE(JSONB_AGG(
      JSONB_BUILD_OBJECT('cost_center_eng',cost_center_eng,'cost_center_description',cost_center_description,'total',total)
      ORDER BY total DESC), '[]'::jsonb)
    FROM (
      SELECT MAX(cost_center_eng) AS cost_center_eng, MAX(cost_center_description) AS cost_center_description, SUM(amount) AS total
      FROM base WHERE cost_center_description IN ('BBA','HLD','SCI','SS','THM','FAA','MBA','MM')
      GROUP BY cost_center_description
    ) c
  ),
  'pivot_table_by_gl_detail_division', (
    SELECT COALESCE(JSONB_AGG(
      JSONB_BUILD_OBJECT('gl_id',gl_id,'gl_description',gl_description,'total_amount',total_amount,'details_breakdown',details_breakdown)
      ORDER BY gl_id), '[]'::jsonb)
    FROM (
      SELECT gl_id, MAX(gl_description) AS gl_description, SUM(detail_amount) AS total_amount,
        COALESCE(JSONB_AGG(JSONB_BUILD_OBJECT('details',details,'amount',detail_amount) ORDER BY detail_amount DESC),'[]'::jsonb) AS details_breakdown
      FROM (
        SELECT gl_id, gl_description, details, cost_own_description, SUM(amount) AS detail_amount
        FROM base WHERE cost_center_description IN ('BBA','HLD','SCI','SS','THM','FAA','MBA','MM')
        GROUP BY gl_id, gl_description, details, cost_own_description
      ) d GROUP BY gl_id
    ) x
  ),
  'table_by_gl_all', (
    SELECT COALESCE(JSONB_AGG(
      JSONB_BUILD_OBJECT('gl_id',gl_id,'gl_description',gl_description,'gl_group',gl_group,'total',total)
      ORDER BY gl_group), '[]'::jsonb)
    FROM (
      SELECT gl_id, gl_description, cost_own_description, MAX(gl_group) AS gl_group, SUM(amount) AS total
      FROM base GROUP BY gl_id, gl_description, cost_own_description
    ) g
  ),
  'table_by_cost_center_all', (
    SELECT COALESCE(JSONB_AGG(
      JSONB_BUILD_OBJECT('cost_center_eng',cost_center_eng,'cost_center_description',cost_center_description,'total',total)
      ORDER BY total DESC), '[]'::jsonb)
    FROM (
      SELECT MAX(cost_center_eng) AS cost_center_eng, MAX(cost_center_description) AS cost_center_description, SUM(amount) AS total
      FROM base GROUP BY cost_center_description
    ) c
  ),
  'pivot_table_by_gl_detail_all', (
    SELECT COALESCE(JSONB_AGG(
      JSONB_BUILD_OBJECT('gl_id',gl_id,'gl_description',gl_description,'total_amount',total_amount,'details_breakdown',details_breakdown)
      ORDER BY gl_id), '[]'::jsonb)
    FROM (
      SELECT gl_id, MAX(gl_description) AS gl_description, SUM(detail_amount) AS total_amount,
        COALESCE(JSONB_AGG(JSONB_BUILD_OBJECT('details',details,'amount',detail_amount) ORDER BY detail_amount DESC),'[]'::jsonb) AS details_breakdown
      FROM (
        SELECT gl_id, gl_description, details, cost_own_description, SUM(amount) AS detail_amount
        FROM base GROUP BY gl_id, gl_description, details, cost_own_description
      ) d GROUP BY gl_id
    ) x
  )
) AS payload
"""

# ── SQL: IO dashboard ─────────────────────────────────────────────────────────

_SQL_IO = """
WITH base AS (
  SELECT
    erp.fiscal_year,
    erp.io_goods,
    good.io_good_description                           AS io_goods_description,
    erp.io_project,
    project.io_project_description,
    erp.io_work,
    work.io_work_description,
    COALESCE(NULLIF(TRIM(erp.cost_owner),''),'Other') AS cost_owner,
    TRIM(costOwn.cost_center_eng)                      AS cost_own_eng,
    TRIM(costOwn.cost_center_description)              AS cost_own_description,
    TRIM(costCtr.cost_center_eng)                      AS cost_center_eng,
    TRIM(costCtr.cost_center_description)              AS cost_center_description,
    erp.order_description,
    erp.details,
    erp.amount,
    erp.fiscal_month,
    MOD(erp.month + 5, 12) + 1                                    AS pa_month,
    CASE WHEN erp.month >= 7 THEN erp.year ELSE erp.year - 1 END  AS pa_year
  FROM erp_2025 erp
    LEFT JOIN master_io_goods   good    ON good.io_good_id       = erp.io_goods
    LEFT JOIN master_io_project project ON project.io_project_id = erp.io_project
    LEFT JOIN master_io_work    work    ON work.io_work_id        = erp.io_work
    LEFT JOIN master_cost_ctr   costOwn ON erp.cost_owner         = costOwn.cost_center_id
    LEFT JOIN master_cost_ctr   costCtr ON erp.cost_ctr_id        = costCtr.cost_center_id
  WHERE (
      (%(pa_year)s IS NULL     AND erp.fiscal_year = %(year)s)
      OR (%(pa_year)s IS NOT NULL AND CASE WHEN erp.month >= 7 THEN erp.year ELSE erp.year - 1 END = %(pa_year)s)
    )
    AND (%(month_from)s IS NULL OR CASE WHEN %(pa_year)s IS NULL THEN erp.fiscal_month ELSE MOD(erp.month + 5, 12) + 1 END >= %(month_from)s)
    AND (%(month_to)s   IS NULL OR CASE WHEN %(pa_year)s IS NULL THEN erp.fiscal_month ELSE MOD(erp.month + 5, 12) + 1 END <= %(month_to)s)
    AND (%(cost_center)s IS NULL OR costCtr.cost_center_description ILIKE %(cost_center_like)s)
    AND (%(cost_owner)s  IS NULL
         OR TRIM(erp.cost_owner) = %(cost_owner)s
         OR costOwn.cost_center_description ILIKE %(cost_owner_like)s
         OR (%(ea_cost_center)s IS NOT NULL
             AND costOwn.cost_center_description ILIKE 'EA'
             AND UPPER(TRIM(costCtr.cost_center_description)) = %(ea_cost_center)s))
    AND (%(q)s IS NULL
         OR erp.details                    ILIKE %(q_like)s
         OR erp.order_description          ILIKE %(q_like)s
         OR good.io_good_description       ILIKE %(q_like)s
         OR project.io_project_description ILIKE %(q_like)s
         OR work.io_work_description       ILIKE %(q_like)s)
)
SELECT JSONB_BUILD_OBJECT(
  'kpis', JSONB_BUILD_OBJECT(
    'total_amount',           (SELECT COALESCE(SUM(amount),0) FROM base),
    'total_budget',           900000000,
    'total_amount_io_goods',  (SELECT COALESCE(SUM(amount),0) FROM base WHERE base.io_goods IS NOT NULL),
    'count_io_goods',         (SELECT COUNT(DISTINCT io_goods) FROM base WHERE base.io_goods IS NOT NULL),
    'total_amount_io_project',(SELECT COALESCE(SUM(amount),0) FROM base WHERE base.io_project IS NOT NULL),
    'count_io_project',       (SELECT COUNT(DISTINCT io_project) FROM base WHERE base.io_project IS NOT NULL)
  ),
  'spending_by_dept', (
    SELECT COALESCE(JSONB_AGG(
      JSONB_BUILD_OBJECT('cost_center_eng',cost_center_eng,'cost_center_description',cost_center_description,'total',total)
      ORDER BY total DESC), '[]'::jsonb)
    FROM (
      SELECT MAX(cost_center_eng) AS cost_center_eng, MAX(cost_center_description) AS cost_center_description, SUM(amount) AS total
      FROM base WHERE cost_center_description NOT IN ('BBA','HLD','SCI','SS','THM','FAA','MBA','MM')
      GROUP BY cost_center_description
    ) c
  ),
  'spending_by_division', (
    SELECT COALESCE(JSONB_AGG(
      JSONB_BUILD_OBJECT('cost_center_eng',cost_center_eng,'cost_center_description',cost_center_description,'total',total)
      ORDER BY total DESC), '[]'::jsonb)
    FROM (
      SELECT MAX(cost_center_eng) AS cost_center_eng, MAX(cost_center_description) AS cost_center_description, SUM(amount) AS total
      FROM base WHERE cost_center_description IN ('BBA','HLD','SCI','SS','THM','FAA','MBA','MM')
      GROUP BY cost_center_description
    ) c
  ),
  'pivot_table_by_io_goods', (
    SELECT COALESCE(JSONB_AGG(
      JSONB_BUILD_OBJECT('io_goods',io_goods,'io_goods_description',io_goods_description,'total_amount',total_amount,'order_breakdown',order_breakdown)
      ORDER BY io_goods), '[]'::jsonb)
    FROM (
      SELECT io_goods, MAX(io_goods_description) AS io_goods_description, SUM(order_amount) AS total_amount,
        COALESCE(JSONB_AGG(JSONB_BUILD_OBJECT('order_description',order_description,'details',details,'amount',order_amount) ORDER BY io_goods),'[]'::jsonb) AS order_breakdown
      FROM (
        SELECT io_goods, io_goods_description, order_description, details, SUM(amount) AS order_amount
        FROM base GROUP BY io_goods, io_goods_description, details, order_description
      ) d WHERE io_goods IS NOT NULL
      GROUP BY io_goods
    ) x
  ),
  'pivot_table_by_io_project', (
    SELECT COALESCE(JSONB_AGG(
      JSONB_BUILD_OBJECT('io_project',io_project,'io_project_description',io_project_description,'total_amount',total_amount,'order_breakdown',order_breakdown)
      ORDER BY io_project), '[]'::jsonb)
    FROM (
      SELECT io_project, MAX(io_project_description) AS io_project_description, SUM(order_amount) AS total_amount,
        COALESCE(JSONB_AGG(JSONB_BUILD_OBJECT('order_description',order_description,'details',details,'amount',order_amount) ORDER BY io_project),'[]'::jsonb) AS order_breakdown
      FROM (
        SELECT io_project, io_project_description, order_description, details, SUM(amount) AS order_amount
        FROM base GROUP BY io_project, io_project_description, details, order_description
      ) d WHERE io_project IS NOT NULL
      GROUP BY io_project
    ) x
  ),
  'pivot_table_by_io_work', (
    SELECT COALESCE(JSONB_AGG(
      JSONB_BUILD_OBJECT('io_work',io_work,'io_work_description',io_work_description,'total_amount',total_amount,'order_breakdown',order_breakdown)
      ORDER BY io_work), '[]'::jsonb)
    FROM (
      SELECT io_work, MAX(io_work_description) AS io_work_description, SUM(order_amount) AS total_amount,
        COALESCE(JSONB_AGG(JSONB_BUILD_OBJECT('order_description',order_description,'details',details,'amount',order_amount) ORDER BY io_work),'[]'::jsonb) AS order_breakdown
      FROM (
        SELECT io_work, io_work_description, order_description, details, SUM(amount) AS order_amount
        FROM base GROUP BY io_work, io_work_description, details, order_description
      ) d WHERE io_work IS NOT NULL
      GROUP BY io_work
    ) x
  )
) AS payload
"""


# ── Helpers ───────────────────────────────────────────────────────────────────

def _build_dashboard_params(
    p: FinanceQueryParams,
    role: str,
    cost_owner_override: str | None = None,
) -> dict:
    cost_owner = cost_owner_override
    if cost_owner is None and not is_fa(role):
        cost_owner = role.upper()

    ilike_root = ILIKE_ROOT_OVERRIDE.get(role, cost_owner)
    ea_cost_center = role.upper() if is_division(role) else None

    return {
        "year":             p.year,
        "month_from":       p.month_from,
        "month_to":         p.month_to,
        "pa_year":          p.pa_year,
        "gl_group":         p.gl_group or None,
        "cost_center":      p.cost_center or None,
        "cost_center_like": f"%{p.cost_center}%" if p.cost_center else None,
        "cost_owner":       cost_owner,
        "cost_owner_like":  f"%{ilike_root}%" if ilike_root else None,
        "ea_cost_center":   ea_cost_center,
        "q":                p.q or None,
        "q_like":           f"%{p.q}%" if p.q else None,
    }


def _build_io_params(p: IOQueryParams, role: str) -> dict:
    cost_owner = p.cost_owner or None
    if cost_owner is None and not is_fa(role):
        cost_owner = role.upper()
    ilike_root = ILIKE_ROOT_OVERRIDE.get(role, cost_owner)
    ea_cost_center = role.upper() if is_division(role) else None

    return {
        "year":             p.year,
        "month_from":       p.month_from,
        "month_to":         p.month_to,
        "pa_year":          p.pa_year,
        "cost_owner":       cost_owner,
        "cost_owner_like":  f"%{ilike_root}%" if ilike_root else None,
        "ea_cost_center":   ea_cost_center,
        "cost_center":      p.cost_center or None,
        "cost_center_like": f"%{p.cost_center}%" if p.cost_center else None,
        "q":                p.q or None,
        "q_like":           f"%{p.q}%" if p.q else None,
    }


async def _run_query(sql: str, params: dict, label: str) -> dict:
    async with get_db() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql, params)
            row = await cur.fetchone()
            payload = row[0] if row else {}
            if isinstance(payload, str):
                import json
                payload = json.loads(payload)
            return payload


# ── Public API ────────────────────────────────────────────────────────────────

async def get_dashboard(
    role: str,
    params: FinanceQueryParams,
    cache_prefix: str = "finance",
) -> dict:
    from app.core.security import params_hash
    db_params = _build_dashboard_params(params, role, params.cost_owner or None)
    cache_key = f"seamless:v1:{cache_prefix}:{role}:{params_hash(db_params)}"

    cached = await get_cached(cache_key)
    if cached is not None:
        return cached

    try:
        result = await _run_query(_SQL_DASHBOARD, db_params, cache_prefix)
    except Exception as exc:
        logger.error("%s query failed: %s", cache_prefix, exc)
        raise

    await set_cached(cache_key, result, settings.redis_ttl_default)
    return result


async def get_io(role: str, params: IOQueryParams) -> dict:
    from app.core.security import params_hash
    db_params = _build_io_params(params, role)
    cache_key = f"seamless:v1:io:{role}:{params_hash(db_params)}"

    cached = await get_cached(cache_key)
    if cached is not None:
        return cached

    try:
        result = await _run_query(_SQL_IO, db_params, "IO")
    except Exception as exc:
        logger.error("IO query failed: %s", exc)
        raise

    await set_cached(cache_key, result, settings.redis_ttl_default)
    return result
