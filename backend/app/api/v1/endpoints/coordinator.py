from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.v1.deps import require_fa_with_position
from app.core.logging import get_logger
from app.schemas.common import PaginatedResponse
from app.schemas.coordinator import CoordinatorCreate, CoordinatorResponse
from app.services import coordinator_service

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
    response_model=CoordinatorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add or reactivate a coordinator (FA + position required)",
    responses={
        400: {"description": "Invalid username"},
        409: {"description": "Username already exists (will reactivate instead)"},
    },
)
async def add_coordinator(body: CoordinatorCreate, user: dict = Depends(require_fa_with_position)):
    try:
        return await coordinator_service.add_coordinator(
            username=body.username,
            created_by=user["sub"],
        )
    except Exception as exc:
        logger.error("Add coordinator failed: %s", exc)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Operation failed")


@router.patch(
    "/{coord_id}",
    response_model=CoordinatorResponse,
    summary="Toggle coordinator active/inactive — FA + position required",
    responses={
        404: {"description": "Coordinator not found"},
    },
)
async def toggle_coordinator(coord_id: int, user: dict = Depends(require_fa_with_position)):
    try:
        result = await coordinator_service.toggle_coordinator(
            coord_id=coord_id,
            updated_by=user["sub"],
        )
    except Exception as exc:
        logger.error("Toggle coordinator failed: %s", exc)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Operation failed")

    if result is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Coordinator not found")
    return result
