from datetime import datetime

from pydantic import BaseModel, Field


class CoordinatorCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=100, pattern=r"^[\w\-\.@]+$")


class CoordinatorResponse(BaseModel):
    id: int
    username: str
    active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
    created_by: str | None = None
    updated_by: str | None = None

    model_config = {"from_attributes": True}
