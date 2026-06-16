from fastapi import APIRouter

from app.api.v1.endpoints import auth, coordinator, finance, io

v1_router = APIRouter()

v1_router.include_router(auth.router)
v1_router.include_router(finance.router)
v1_router.include_router(io.router)
v1_router.include_router(coordinator.router)
