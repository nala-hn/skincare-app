from pydantic import BaseModel, EmailStr, computed_field
from typing import Optional
from datetime import datetime, date
from ..core.utils import calculate_age

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    alias: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    skin_type: Optional[str] = None

class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    alias: Optional[str]
    date_of_birth: Optional[date]
    gender: Optional[str]
    skin_type: Optional[str]
    created_at: datetime

    @computed_field
    @property
    def age(self) -> Optional[int]:
        return calculate_age(self.date_of_birth)

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str