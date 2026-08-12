from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.database import get_session
from app.schemas.generated_schemas import (
    MaterialTypeCreate,
    MaterialTypeRead,
    MaterialStockCreate,
    MaterialStockRead,
    MaterialStockUpdate,
    DiceJobColourCreate,
    DiceJobColourRead,
)
from app.services.material_service import (
    create_material_type,
    get_material_type,
    list_material_types,
    update_material_type,
    delete_material_type,
    create_material_stock,
    get_material_stock,
    list_material_stocks,
    update_material_stock,
    delete_material_stock,
    create_dice_job_colour,
    get_dice_job_colour,
    list_dice_job_colours,
    update_dice_job_colour,
    delete_dice_job_colour,
)

router = APIRouter()

# MaterialType endpoints
@router.post("/material-types", response_model=MaterialTypeRead)
async def create_type(m: MaterialTypeCreate, db=Depends(get_session)):
    return await create_material_type(db, m)

@router.get("/material-types/{material_type_id}", response_model=MaterialTypeRead)
async def read_type(material_type_id: int, db=Depends(get_session)):
    db_obj = await get_material_type(db, material_type_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Not found")
    return db_obj

@router.get("/material-types", response_model=List[MaterialTypeRead])
async def read_types(skip: int = 0, limit: int = 100, db=Depends(get_session)):
    return await list_material_types(db, skip, limit)

@router.put("/material-types/{material_type_id}", response_model=MaterialTypeRead)
async def update_type(material_type_id: int, m: MaterialTypeCreate, db=Depends(get_session)):
    db_obj = await update_material_type(db, material_type_id, m)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Not found")
    return db_obj

@router.delete("/material-types/{material_type_id}", status_code=204)
async def delete_type(material_type_id: int, db=Depends(get_session)):
    await delete_material_type(db, material_type_id)
    return

# MaterialStock endpoints
@router.post("/material-stocks", response_model=MaterialStockRead)
async def create_stock(s: MaterialStockCreate, db=Depends(get_session)):
    return await create_material_stock(db, s)

@router.get("/material-stocks/{material_stock_id}", response_model=MaterialStockRead)
async def read_stock(material_stock_id: int, db=Depends(get_session)):
    db_obj = await get_material_stock(db, material_stock_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Not found")
    return db_obj

@router.get("/material-stocks", response_model=List[MaterialStockRead])
async def read_stocks(skip: int = 0, limit: int = 100, db=Depends(get_session)):
    return await list_material_stocks(db, skip, limit)

@router.patch("/material-stocks/{material_stock_id}", response_model=MaterialStockRead)
async def patch_stock(material_stock_id: int, s: MaterialStockUpdate, db=Depends(get_session)):
    db_obj = await update_material_stock(db, material_stock_id, s)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Not found")
    return db_obj

@router.delete("/material-stocks/{material_stock_id}", status_code=204)
async def delete_stock(material_stock_id: int, db=Depends(get_session)):
    await delete_material_stock(db, material_stock_id)
    return

# DiceJobColour endpoints
@router.post("/dice-job-colours", response_model=DiceJobColourRead)
async def create_colour(c: DiceJobColourCreate, db=Depends(get_session)):
    return await create_dice_job_colour(db, c)

@router.get("/dice-job-colours/{dice_job_colour_id}", response_model=DiceJobColourRead)
async def read_colour(dice_job_colour_id: int, db=Depends(get_session)):
    db_obj = await get_dice_job_colour(db, dice_job_colour_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Not found")
    return db_obj

@router.get("/dice-job-colours", response_model=List[DiceJobColourRead])
async def read_colours(skip: int = 0, limit: int = 100, db=Depends(get_session)):
    return await list_dice_job_colours(db, skip, limit)

@router.put("/dice-job-colours/{dice_job_colour_id}", response_model=DiceJobColourRead)
async def update_colour(dice_job_colour_id: int, c: DiceJobColourCreate, db=Depends(get_session)):
    db_obj = await update_dice_job_colour(db, dice_job_colour_id, c)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Not found")
    return db_obj

@router.delete("/dice-job-colours/{dice_job_colour_id}", status_code=204)
async def delete_colour(dice_job_colour_id: int, db=Depends(get_session)):
    await delete_dice_job_colour(db, dice_job_colour_id)
    return
