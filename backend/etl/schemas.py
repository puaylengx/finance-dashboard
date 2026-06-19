"""Pydantic validation schemas for ERP transaction rows."""
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, field_validator


class ErpTransactionRow(BaseModel):
    fiscal_year:       int
    fiscal_month:      int
    trimester:         int
    day:               int
    month:             int
    year:              int
    doc_no:            int
    doc_date:          date
    funds_ctr:         str
    cost_ctr_id:       str
    cost_owner:        str | None = None
    cost_note:         str | None = None
    io_goods:          str | None = None
    io_work:           str | None = None
    io_activity:       str | None = None
    io_project:        str | None = None
    order_description: str | None = None
    hr_ot:             str | None = None
    gl_id:             str
    gl_description:    str
    amount:            Decimal
    details:           str
    mu_strategy:       Decimal | None = None
    ic_strategy:       Decimal | None = None

    @field_validator("fiscal_year")
    @classmethod
    def validate_fiscal_year(cls, v: int) -> int:
        if not (2000 <= v <= 2100):
            raise ValueError(f"fiscal_year {v} out of range 2000–2100")
        return v

    @field_validator("fiscal_month")
    @classmethod
    def validate_fiscal_month(cls, v: int) -> int:
        # ERP fiscal months can extend beyond 12 (period 13–16 for adjustments)
        if not (1 <= v <= 16):
            raise ValueError(f"fiscal_month {v} out of range 1–16")
        return v

    @field_validator("month")
    @classmethod
    def validate_month(cls, v: int) -> int:
        if not (1 <= v <= 12):
            raise ValueError(f"month {v} out of range 1–12")
        return v

    @field_validator("gl_id", "cost_ctr_id", "funds_ctr")
    @classmethod
    def strip_required_str(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("field must not be empty after stripping whitespace")
        return v
