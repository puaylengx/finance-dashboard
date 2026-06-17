from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.v1.deps import get_current_user
from app.core.logging import get_logger
from app.schemas.finance import IOQueryParams
from app.services import finance_service
from app.services.finance_service import _IO_TABLE_KEYS, _apply_top_n

router = APIRouter(tags=["IO"])
logger = get_logger(__name__)


@router.get(
    "/io",
    summary="IO (Internal Order) dashboard — all authenticated users",
    responses={
        401: {"description": "Not authenticated"},
    },
)
async def get_io(
    year: int = Query(default=2025, ge=2000, le=2100),
    month_from: int | None = Query(default=None, ge=1, le=12),
    month_to: int | None = Query(default=None, ge=1, le=12),
    pa_year: int | None = Query(default=None, ge=2000, le=2100),
    cost_owner: str | None = Query(default=None),
    cost_center: str | None = Query(default=None),
    q: str | None = Query(default=None, max_length=200),
    top_n: int | None = Query(default=None, ge=1, le=500, description="Limit rows in each table array"),
    user: dict = Depends(get_current_user),
):
    params = IOQueryParams(
        year=year, month_from=month_from, month_to=month_to, pa_year=pa_year,
        cost_owner=cost_owner, cost_center=cost_center, q=q, top_n=top_n,
    )
    try:
        result = await finance_service.get_io(role=user["role"], params=params)
        return _apply_top_n(result, _IO_TABLE_KEYS, top_n)
    except Exception as exc:
        logger.error("IO endpoint error: %s", exc)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Query failed")
