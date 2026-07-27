from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models import generated_models as models
from app.schemas.generated_schemas import (
    MaterialTypeCreate,
    MaterialTypeRead,
    MaterialStockCreate,
    MaterialStockUpdate,
    DiceJobColourCreate,
)

async def create_material_type(db: AsyncSession, m: MaterialTypeCreate) -> models.MaterialType:
    db_obj = models.MaterialType(code=m.code, description=m.description)
    db.add(db_obj)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise
    await db.refresh(db_obj)
    return db_obj

async def get_material_type(db: AsyncSession, material_type_id: int) -> Optional[models.MaterialType]:
    return await db.get(models.MaterialType, material_type_id)

async def list_material_types(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.MaterialType]:
    result = await db.execute(select(models.MaterialType).offset(skip).limit(limit))
    return result.scalars().all()

async def update_material_type(db: AsyncSession, material_type_id: int, m: MaterialTypeCreate) -> Optional[models.MaterialType]:
    db_obj = await db.get(models.MaterialType, material_type_id)
    if not db_obj:
        return None
    db_obj.code = m.code
    db_obj.description = m.description
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def delete_material_type(db: AsyncSession, material_type_id: int) -> None:
    db_obj = await db.get(models.MaterialType, material_type_id)
    if not db_obj:
        return
    await db.delete(db_obj)
    await db.commit()

# MaterialStock
async def create_material_stock(db: AsyncSession, s: MaterialStockCreate) -> models.MaterialStock:
    db_obj = models.MaterialStock(
        colour_name=s.colour_name,
        material_type_id=s.material_type_id,
        quantity_in_stock=s.quantity_in_stock,
        is_active=s.is_active,
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def get_material_stock(db: AsyncSession, material_stock_id: int) -> Optional[models.MaterialStock]:
    return await db.get(models.MaterialStock, material_stock_id)

async def list_material_stocks(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.MaterialStock]:
    result = await db.execute(select(models.MaterialStock).offset(skip).limit(limit))
    return result.scalars().all()

async def update_material_stock(db: AsyncSession, material_stock_id: int, s: MaterialStockUpdate) -> Optional[models.MaterialStock]:
    db_obj = await db.get(models.MaterialStock, material_stock_id)
    if not db_obj:
        return None
    for field, value in s.dict(exclude_unset=True).items():
        setattr(db_obj, field, value)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def delete_material_stock(db: AsyncSession, material_stock_id: int) -> None:
    db_obj = await db.get(models.MaterialStock, material_stock_id)
    if not db_obj:
        return
    await db.delete(db_obj)
    await db.commit()

# DiceJobColour
async def create_dice_job_colour(db: AsyncSession, c: DiceJobColourCreate) -> models.DiceJobColour:
    db_obj = models.DiceJobColour(
        dice_job_id=c.dice_job_id,
        material_stock_id=c.material_stock_id,
        colour_order=c.colour_order,
    )
    db.add(db_obj)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise
    await db.refresh(db_obj)
    return db_obj

async def get_dice_job_colour(db: AsyncSession, dice_job_colour_id: int) -> Optional[models.DiceJobColour]:
    return await db.get(models.DiceJobColour, dice_job_colour_id)

async def list_dice_job_colours(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.DiceJobColour]:
    result = await db.execute(select(models.DiceJobColour).offset(skip).limit(limit))
    return result.scalars().all()

async def update_dice_job_colour(db: AsyncSession, dice_job_colour_id: int, c: DiceJobColourCreate) -> Optional[models.DiceJobColour]:
    db_obj = await db.get(models.DiceJobColour, dice_job_colour_id)
    if not db_obj:
        return None
    for field, value in c.dict(exclude_unset=True).items():
        setattr(db_obj, field, value)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def delete_dice_job_colour(db: AsyncSession, dice_job_colour_id: int) -> None:
    db_obj = await db.get(models.DiceJobColour, dice_job_colour_id)
    if not db_obj:
        return
    await db.delete(db_obj)
    await db.commit()
