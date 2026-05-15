"""API v1 router."""

from fastapi import APIRouter

from app.api.v1.admin.routes import router as admin_router
from app.api.v1.auth.routes import router as auth_router
from app.api.v1.tenant_admin.routes import router as tenant_admin_router
from app.api.v1.tenant_admin.settings_routes import router as tenant_admin_settings_router
from app.api.v1.users.routes import router as users_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth")
api_router.include_router(users_router, prefix="/users")
api_router.include_router(admin_router, prefix="/admin")
api_router.include_router(tenant_admin_router, prefix="/tenant-admin")
api_router.include_router(tenant_admin_settings_router, prefix="/tenant-admin")
