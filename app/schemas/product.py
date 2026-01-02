from pydantic import BaseModel, computed_field
from typing import Optional, List
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

class ProductBase(BaseModel):
    product_name: str
    brand: Optional[str] = None
    category_id: int
    pao_months: int = 12
    opened_at: Optional[date] = None

class ProductCreate(ProductBase):
    ingredient_ids: Optional[List[int]] = []

class ProductOut(ProductBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime

    @computed_field
    @property
    def expiry_date(self) -> Optional[date]:
        if self.opened_at:
            return self.opened_at + relativedelta(months=self.pao_months)
        return None

    @computed_field
    @property
    def days_left(self) -> Optional[int]:
        if self.opened_at:
            expiry = self.opened_at + relativedelta(months=self.pao_months)
            delta = expiry - date.today()
            return delta.days
        return None

    class Config:
        from_attributes = True
        

class IngredientOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True