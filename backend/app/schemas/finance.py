from pydantic import BaseModel, Field


class FinanceQueryParams(BaseModel):
    year: int = Field(default=2025, ge=2000, le=2100)
    month_from: int | None = Field(default=None, ge=1, le=12)
    month_to: int | None = Field(default=None, ge=1, le=12)
    pa_year: int | None = Field(default=None, ge=2000, le=2100)
    gl_group: str | None = None
    cost_center: str | None = None
    cost_owner: str | None = None
    q: str | None = None
    top_n: int | None = Field(default=None, ge=1, le=500, description="Limit rows returned in each table array")


class IOQueryParams(BaseModel):
    year: int = Field(default=2025, ge=2000, le=2100)
    month_from: int | None = Field(default=None, ge=1, le=12)
    month_to: int | None = Field(default=None, ge=1, le=12)
    pa_year: int | None = Field(default=None, ge=2000, le=2100)
    cost_owner: str | None = None
    cost_center: str | None = None
    q: str | None = None
    top_n: int | None = Field(default=None, ge=1, le=500, description="Limit rows returned in each table array")
