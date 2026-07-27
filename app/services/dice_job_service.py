from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import generated_models as models
from app.schemas.generated_schemas import DiceJobCreate

async def create_dice_job(db: AsyncSession, job: DiceJobCreate) -> models.DiceJob:
    db_obj = models.DiceJob(
        job_name=job.job_name,
        job_date=job.job_date,
        colour_count=job.colour_count,
        production_method_id=job.production_method_id,
        description=job.description,
        primary_material_stock_id=job.primary_material_stock_id,
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def get_dice_job(db: AsyncSession, job_id: int) -> Optional[models.DiceJob]:
    return await db.get(models.DiceJob, job_id)

async def list_dice_jobs(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.DiceJob]:
    result = await db.execute(select(models.DiceJob).offset(skip).limit(limit))
    return result.scalars().all()

async def update_dice_job(db: AsyncSession, job_id: int, job: DiceJobCreate) -> Optional[models.DiceJob]:
    db_obj = await db.get(models.DiceJob, job_id)
    if not db_obj:
        return None
    for field, value in job.dict(exclude_unset=True).items():
        setattr(db_obj, field, value)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def delete_dice_job(db: AsyncSession, job_id: int) -> None:
    db_obj = await db.get(models.DiceJob, job_id)
    if not db_obj:
        return
    await db.delete(db_obj)
    await db.commit()
