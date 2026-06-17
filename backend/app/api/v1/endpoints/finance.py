from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.v1.deps import get_current_user, require_fa
from app.core.logging import get_logger
from app.schemas.finance import FinanceQueryParams
from app.services import finance_service
from app.services.finance_service import _FINANCE_TABLE_KEYS, _apply_top_n

router = APIRouter(tags=["Finance"])
logger = get_logger(__name__)


@router.get(
    "/finance",
    summary="FA-only finance dashboard (dept + division breakdown)",
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "FA role required"},
    },
)
async def get_finance(
    year: int = Query(default=2025, ge=2000, le=2100),
    month_from: int | None = Query(default=None, ge=1, le=12),
    month_to: int | None = Query(default=None, ge=1, le=12),
    pa_year: int | None = Query(default=None, ge=2000, le=2100),
    gl_group: str | None = Query(default=None),
    cost_center: str | None = Query(default=None),
    cost_owner: str | None = Query(default=None),
    q: str | None = Query(default=None, max_length=200),
    top_n: int | None = Query(default=None, ge=1, le=500, description="Limit rows in each table array"),
    user: dict = Depends(require_fa),
):
    params = FinanceQueryParams(
        year=year, month_from=month_from, month_to=month_to, pa_year=pa_year,
        gl_group=gl_group, cost_center=cost_center, cost_owner=cost_owner, q=q, top_n=top_n,
    )
    try:
        result = await finance_service.get_dashboard(
            role=user["role"], params=params, cache_prefix="finance"
        )
        return _apply_top_n(result, _FINANCE_TABLE_KEYS, top_n)
    except Exception as exc:
        logger.error("Finance endpoint error: %s", exc)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Query failed")


@router.get(
    "/budget",
    summary="All-authenticated budget dashboard",
    responses={
        401: {"description": "Not authenticated"},
    },
)
async def get_budget(
    year: int = Query(default=2025, ge=2000, le=2100),
    month_from: int | None = Query(default=None, ge=1, le=12),
    month_to: int | None = Query(default=None, ge=1, le=12),
    pa_year: int | None = Query(default=None, ge=2000, le=2100),
    gl_group: str | None = Query(default=None),
    cost_center: str | None = Query(default=None),
    cost_owner: str | None = Query(default=None),
    q: str | None = Query(default=None, max_length=200),
    top_n: int | None = Query(default=None, ge=1, le=500, description="Limit rows in each table array"),
    user: dict = Depends(get_current_user),
):
    params = FinanceQueryParams(
        year=year, month_from=month_from, month_to=month_to, pa_year=pa_year,
        gl_group=gl_group, cost_center=cost_center, cost_owner=cost_owner, q=q, top_n=top_n,
    )
    try:
        result = await finance_service.get_dashboard(
            role=user["role"], params=params, cache_prefix="budget"
        )
        return _apply_top_n(result, _FINANCE_TABLE_KEYS, top_n)
    except Exception as exc:
        logger.error("Budget endpoint error: %s", exc)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Query failed")
