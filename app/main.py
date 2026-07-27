from fastapi import FastAPI

from app.api import dice_jobs as api_dice_jobs
from app.api import materials as api_materials
from app.db import init_db

app = FastAPI(title="Dice Calculator API")
app.include_router(api_dice_jobs.router, prefix="/api")
app.include_router(api_materials.router, prefix="/api")

@app.on_event("startup")
async def startup():
    await init_db()


# To run locally: uvicorn app.main:app --reload
