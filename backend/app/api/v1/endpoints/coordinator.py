from fastapi import APIRouter, Depends, HTTPException, status

from app.api.v1.deps import require_fa_with_position
from app.core.logging import get_logger
from app.schemas.coordinator import CoordinatorCreate, CoordinatorResponse
from app.services import coordinator_service

router = APIRouter(prefix="/admin/coordinators", tags=["Coordinator Management"])
logger = get_logger(__name__)


@router.get(
    "",
    response_model=list[CoordinatorResponse],
    summary="List all coordinators (FA + position required)",
)
async def list_coordinators(user: dict = Depends(require_fa_with_position)):
    try:
        return await coordinator_service.list_coordinators()
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
