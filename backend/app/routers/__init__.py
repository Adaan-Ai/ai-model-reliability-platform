"""
Export all API routers
"""

from app.routers.users import router as users_router
from app.routers.data_sources import router as data_sources_router
from app.routers.datasets import router as datasets_router
from app.routers.quality import router as quality_router
from app.routers.models import router as models_router
from app.routers.evaluations import router as evaluations_router
from app.routers.drift import router as drift_router
from app.routers.reliability import router as reliability_router
from app.routers.reports import router as reports_router
from app.routers.dashboard import router as dashboard_router

__all__ = [
    "users_router",
    "data_sources_router",
    "datasets_router",
    "quality_router",
    "models_router",
    "evaluations_router",
    "drift_router",
    "reliability_router",
    "reports_router",
    "dashboard_router",
]
