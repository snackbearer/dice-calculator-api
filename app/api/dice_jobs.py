from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.db import get_session
from app.schemas.generated_schemas import DiceJobCreate, DiceJobRead
from app.services.dice_job_service import create_dice_job, get_dice_job, list_dice_jobs, update_dice_job, delete_dice_job

router = APIRouter()

@router.post("/dice-jobs", response_model=DiceJobRead)
async def create_job(job: DiceJobCreate, db=Depends(get_session)):
    return await create_dice_job(db, job)

@router.get("/dice-jobs/{job_id}", response_model=DiceJobRead)
async def read_job(job_id: int, db=Depends(get_session)):
    db_job = await get_dice_job(db, job_id)
    if not db_job:
        raise HTTPException(status_code=404, detail="Not found")
    return db_job

@router.get("/dice-jobs", response_model=List[DiceJobRead])
async def read_jobs(skip: int = 0, limit: int = 100, db=Depends(get_session)):
    return await list_dice_jobs(db, skip, limit)

@router.put("/dice-jobs/{job_id}", response_model=DiceJobRead)
async def update_job(job_id: int, job: DiceJobCreate, db=Depends(get_session)):
    db_job = await update_dice_job(db, job_id, job)
    if not db_job:
        raise HTTPException(status_code=404, detail="Not found")
    return db_job

@router.delete("/dice-jobs/{job_id}", status_code=204)
async def delete_job(job_id: int, db=Depends(get_session)):
    await delete_dice_job(db, job_id)
    return
