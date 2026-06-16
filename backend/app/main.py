from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.api.v1.router import v1_router
from app.core.config import settings
from app.core.database import close_db, init_db
from app.core.logging import get_logger
from app.core.redis_client import close_redis, init_redis

logger = get_logger(__name__)


def _init_sentry() -> None:
    """Sentry เป็น optional — ถ้า DSN ไม่ถูกต้องจะ log warning แทน crash"""
    dsn = settings.sentry_dsn.strip()
    if not dsn or not dsn.startswith("https://"):
        return
    try:
        import sentry_sdk
        sentry_sdk.init(dsn=dsn, traces_sample_rate=0.1)
        logger.info("Sentry initialized")
    except Exception as exc:
        logger.warning("Sentry init skipped: %s", exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s v%s", settings.app_name, settings.app_version)
    await init_db()
    await init_redis()
    _init_sentry()
    yield
    await close_db()
    await close_redis()
    logger.info("Shutdown complete")


limiter = Limiter(key_func=get_remote_address, default_limits=[settings.rate_limit_default])

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "## Seamless Dashboard API\n\n"
        "Financial data visualization API with role-based access control.\n\n"
        "### Authentication\n"
        "- `POST /api/v1/auth/login` — local accounts (dev)\n"
        "- `POST /api/v1/auth/entra-login` — Microsoft Entra ID token exchange\n"
        "- `POST /api/v1/auth/draft-login` — dev simulation\n\n"
        "All protected endpoints require `Authorization: Bearer <token>` header."
    ),
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["X-Request-ID"],
)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if not settings.debug:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception %s %s — %s", request.method, request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "error": "Internal server error"},
    )


app.include_router(v1_router, prefix="/api/v1")


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "version": settings.app_version}
