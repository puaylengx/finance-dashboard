from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api.v1.deps import get_current_user
from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.auth import (
    DraftLoginRequest,
    EntraLoginRequest,
    TokenResponse,
    UserInfo,
)
from app.schemas.common import APIResponse
from app.services.auth_service import (
    EntraNotConfiguredError,
    draft_login,
    login_with_entra_token,
    login_with_password,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = get_logger(__name__)
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/login",
    response_model=APIResponse[TokenResponse],
    summary="Login with username/password (local accounts)",
    responses={
        400: {"description": "Missing credentials"},
        401: {"description": "Invalid credentials"},
    },
)
@limiter.limit(settings.rate_limit_auth)
async def login(request: Request, form: OAuth2PasswordRequestForm = Depends()):
    result = await login_with_password(form.username, form.password)
    if not result:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"success": True, "data": result}


@router.post(
    "/entra-login",
    response_model=APIResponse[TokenResponse],
    summary="Exchange MS Entra ID access token for API JWT (Production)",
    description=(
        "แลก MS Entra ID access token เป็น JWT ของระบบ\n\n"
        "**Flow:**\n"
        "1. Frontend login ผ่าน MSAL → ได้ MS access token\n"
        "2. ส่ง token มาที่ endpoint นี้\n"
        "3. Backend validate กับ Azure JWKS → extract `jobTitle`\n"
        "4. ตรวจสอบ position (chairman/chief/head) หรือ coordinator table\n\n"
        "ต้องตั้งค่า `AZURE_TENANT_ID` และ `AZURE_CLIENT_ID` ใน `.env`\n"
        "หากยังไม่ได้เชื่อมต่อ Azure ให้ใช้ `/auth/draft-login` แทน"
    ),
    responses={
        403: {"description": "Access denied — ไม่มี position หรือไม่ได้เป็น coordinator"},
        503: {"description": "Azure Entra ID ยังไม่ได้ตั้งค่า — ใช้ /draft-login สำหรับ dev"},
    },
)
@limiter.limit(settings.rate_limit_auth)
async def entra_login(request: Request, body: EntraLoginRequest):
    try:
        result = await login_with_entra_token(body.access_token)
    except EntraNotConfiguredError as exc:
        hint = " (ตั้งค่า DRAFT_MODE=true แล้วใช้ /api/v1/auth/draft-login)" if settings.draft_mode else ""
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"MS Entra ID ยังไม่ได้ตั้งค่า{hint}",
        ) from exc

    if result is None:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="ไม่มีสิทธิ์เข้าถึง (โปรดติดต่องานการเงิน หน่วยงบประมาณ)",
        )
    return {"success": True, "data": result}


@router.post(
    "/draft-login",
    response_model=APIResponse[TokenResponse],
    summary="[Draft] Simulate Entra ID login ด้วย job_title (Dev/Staging เท่านั้น)",
    description=(
        "**ใช้สำหรับ Dev/Staging เท่านั้น** — จำลอง MS Entra ID โดยรับ `job_title` โดยตรง\n\n"
        "ใช้ logic การตรวจสอบสิทธิ์เหมือน `/entra-login` ทุกประการ:\n"
        "- `job_title` มี `chairman`, `chief`, หรือ `head` → เข้าได้ (scoped ตาม dept)\n"
        "- `name` อยู่ใน `finance_coordinator` table → เข้าได้\n"
        "- อื่น ๆ → 403\n\n"
        "**ต้องตั้งค่า `DRAFT_MODE=true`** ใน `.env` (default: true)\n"
        "ปิดใน production ด้วย `DRAFT_MODE=false`"
    ),
    responses={
        403: {"description": "Access denied — ไม่มี position หรือไม่ได้เป็น coordinator"},
        404: {"description": "Draft mode ถูกปิดใน production"},
    },
)
@limiter.limit(settings.rate_limit_auth)
async def dev_draft_login(request: Request, body: DraftLoginRequest):
    if not settings.draft_mode:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Not found",
        )

    result = await draft_login(body.job_title, body.name)
    if result is None:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="ไม่มีสิทธิ์เข้าถึง (โปรดติดต่องานการเงิน หน่วยงบประมาณ)",
        )
    return {"success": True, "data": result}


@router.get(
    "/me",
    response_model=APIResponse[UserInfo],
    summary="Get current user info from JWT",
)
async def me(user: dict = Depends(get_current_user)):
    exp_ts = user.get("exp")
    expires_at = (
        datetime.fromtimestamp(exp_ts, tz=timezone.utc).isoformat()
        if exp_ts else None
    )
    return {"success": True, "data": UserInfo(
        username=user.get("sub", ""),
        role=user.get("role", ""),
        position=user.get("position"),
        coordinator=user.get("coordinator", False),
        expires_at=expires_at,
    )}
