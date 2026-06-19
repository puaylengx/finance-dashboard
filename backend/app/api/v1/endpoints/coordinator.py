from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status

from app.api.v1.deps import require_fa_with_position
from app.core.cache import get_idempotency_response, set_idempotency_response
from app.core.logging import get_logger
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.coordinator import CoordinatorCreate, CoordinatorResponse
from app.services import coordinator_service
from app.services.coordinator_service import ConcurrentModificationError

router = APIRouter(prefix="/admin/coordinators", tags=["Coordinator Management"])
logger = get_logger(__name__)


@router.get(
    "",
    response_model=PaginatedResponse[CoordinatorResponse],
    summary="List coordinators with pagination and filtering (FA + position required)",
)
async def list_coordinators(
    q: str | None = Query(default=None, max_length=100, description="Search by username"),
    active: bool | None = Query(default=None, description="Filter by active status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    user: dict = Depends(require_fa_with_position),
):
    try:
        return await coordinator_service.list_coordinators(
            q=q, active=active, page=page, page_size=page_size
        )
    except Exception as exc:
        logger.error("List coordinators failed: %s", exc)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Query failed")


@router.post(
    "",
    response_model=APIResponse[CoordinatorResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Add or reactivate a coordinator (FA + position required)",
    responses={
        400: {"description": "Invalid username"},
        409: {"description": "Username already exists (will reactivate instead)"},
    },
)
async def add_coordinator(
    body: CoordinatorCreate,
    user: dict = Depends(require_fa_with_position),
    idempotency_key: str | None = Header(None, alias="Idempotency-Key", max_length=255),
):
    if idempotency_key:
        cached = await get_idempotency_response(user["sub"], idempotency_key)
        if cached is not None:
            return cached

    try:
        result = await coordinator_service.add_coordinator(
            username=body.username,
            created_by=user["sub"],
        )
        response = {"success": True, "data": result}

        if idempotency_key:
            await set_idempotency_response(user["sub"], idempotency_key, response)

        return response
    except Exception as exc:
        logger.error("Add coordinator failed: %s", exc)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Operation failed")


@router.patch(
    "/{coord_id}",
    response_model=APIResponse[CoordinatorResponse],
    summary="Toggle coordinator active/inactive — FA + position required",
    responses={
        404: {"description": "Coordinator not found"},
        409: {"description": "Record modified by another request — refresh and retry"},
    },
)
async def toggle_coordinator(
    coord_id: int,
    user: dict = Depends(require_fa_with_position),
    x_expected_updated_at: datetime | None = Header(None, alias="X-Expected-Updated-At"),
):
    try:
        result = await coordinator_service.toggle_coordinator(
            coord_id=coord_id,
            updated_by=user["sub"],
            expected_updated_at=x_expected_updated_at,
        )
    except ConcurrentModificationError:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail="Record was modified by another request. Refresh and try again.",
        )
    except Exception as exc:
        logger.error("Toggle coordinator failed: %s", exc)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Operation failed")

    if result is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Coordinator not found")
    return {"success": True, "data": result}
