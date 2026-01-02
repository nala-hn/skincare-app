from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class ProductBase(BaseModel):
    product_name: str
    brand: Optional[str] = None
    category_id: int
    pao_months: int = 12
    opened_at: Optional[date] = None

class ProductCreate(ProductBase):
    pass

class ProductOut(ProductBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True