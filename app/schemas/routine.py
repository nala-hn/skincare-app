from pydantic import BaseModel
from typing import List, Optional
from datetime import time
import enum

from app.schemas.product import ProductOut

class RoutineType(str, enum.Enum):
    MORNING = "morning"
    NIGHT = "night"

class RoutineItemBase(BaseModel):
    product_id: int
    order_index: int = 1

class RoutineItemOut(RoutineItemBase):
    id: int
    order_index: int
    product: Optional[ProductOut]
    class Config:
        from_attributes = True

class RoutineCreate(BaseModel):
    routine_type: RoutineType
    scheduled_time: str

class RoutineOut(BaseModel):
    id: int
    routine_type: RoutineType
    scheduled_time: time
    items: List[RoutineItemOut] = []
    can_combine: bool = True
    conflicts: List[str] = []
    advice: Optional[str] = None

    class Config:
        from_attributes = True

class ConflictCheckRequest(BaseModel):
    product_id_a: int
    product_id_b: int