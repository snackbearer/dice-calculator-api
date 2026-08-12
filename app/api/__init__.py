from fastapi import APIRouter

from .dice_jobs import router as dice_jobs_router
from .materials import router as materials_router

# Aggregate routers from submodules for `from app.api import router`
router = APIRouter()
router.include_router(dice_jobs_router)
router.include_router(materials_router)

