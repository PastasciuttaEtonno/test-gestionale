"""API v1 router."""

from fastapi import APIRouter

from app.api.v1.admin.routes import router as admin_router
from app.api.v1.anagrafiche.routes import router as anagrafiche_router
from app.api.v1.articoli.routes import router as articoli_router
from app.api.v1.auth.routes import router as auth_router
from app.api.v1.events.routes import router as events_router
from app.api.v1.notifications.routes import router as notifications_router
from app.api.v1.bom.routes import router as bom_router
from app.api.v1.dashboard.routes import router as dashboard_router
from app.api.v1.finance.routes import router as finance_router
from app.api.v1.production.routes import router as production_router
from app.api.v1.reports.routes import router as reports_router
from app.api.v1.tasks.routes import router as tasks_router
from app.api.v1.tenant_admin.routes import router as tenant_admin_router
from app.api.v1.tenant_admin.settings_routes import router as tenant_admin_settings_router
from app.api.v1.users.routes import router as users_router

api_router = APIRouter()
api_router.include_router(anagrafiche_router, prefix="/anagrafiche")
api_router.include_router(articoli_router, prefix="/articoli")
api_router.include_router(auth_router, prefix="/auth")
api_router.include_router(events_router, prefix="/events")
api_router.include_router(notifications_router, prefix="/notifications")
api_router.include_router(users_router, prefix="/users")
api_router.include_router(admin_router, prefix="/admin")
api_router.include_router(bom_router, prefix="/bom")
api_router.include_router(dashboard_router, prefix="/dashboard")
api_router.include_router(finance_router, prefix="/finance")
api_router.include_router(production_router, prefix="/production")
api_router.include_router(reports_router, prefix="/reports")
api_router.include_router(tasks_router, prefix="/tasks")
api_router.include_router(tenant_admin_router, prefix="/tenant-admin")
api_router.include_router(tenant_admin_settings_router, prefix="/tenant-admin")
