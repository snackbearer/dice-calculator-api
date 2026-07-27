from pydantic import BaseModel
from typing import Optional, List
import datetime

class MaterialStockBase(BaseModel):
    colour_name: str
    material_type_id: int
    quantity_in_stock: int = 0
    is_active: bool = True

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
