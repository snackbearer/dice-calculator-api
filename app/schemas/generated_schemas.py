from pydantic import BaseModel
from typing import Optional, List
import datetime

class MaterialTypeCreate(BaseModel):
    code: str
    description: Optional[str] = None

class MaterialTypeRead(MaterialTypeCreate):
    material_type_id: int
    created_at: datetime.datetime

    class Config:
        orm_mode = True

class MaterialStockBase(BaseModel):
    colour_name: str
    material_type_id: int
    quantity_in_stock: int = 0
    is_active: bool = True

class MaterialStockCreate(MaterialStockBase):
    pass

class MaterialStockUpdate(BaseModel):
    colour_name: Optional[str] = None
    material_type_id: Optional[int] = None
    quantity_in_stock: Optional[int] = None
    is_active: Optional[bool] = None

class MaterialStockRead(MaterialStockBase):
    material_stock_id: int
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None

    class Config:
        orm_mode = True

class DiceJobCreate(BaseModel):
    job_name: str
    job_date: datetime.date
    colour_count: int
    production_method_id: int
    description: Optional[str] = None
    primary_material_stock_id: Optional[int] = None

class DiceJobRead(DiceJobCreate):
    dice_job_id: int
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None

    class Config:
        orm_mode = True

class DiceJobColourCreate(BaseModel):
    dice_job_id: int
    material_stock_id: int
    colour_order: Optional[int] = None

class DiceJobColourRead(DiceJobColourCreate):
    dice_job_colour_id: int
    created_at: datetime.datetime

    class Config:
        orm_mode = True
