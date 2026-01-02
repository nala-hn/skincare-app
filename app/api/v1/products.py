from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from ...database import models, session
from ...schemas import product as product_schema
from .auth import get_current_user

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/insert", response_model=product_schema.ProductOut)
def create_product(
    product_in: product_schema.ProductCreate, 
    db: Session = Depends(session.get_db),
    current_user: models.User = Depends(get_current_user)
):
    new_product = models.Product(
        **product_in.model_dump(),
        user_id=current_user.id
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.get("/browse", response_model=List[product_schema.ProductOut])
def get_my_products(
    db: Session = Depends(session.get_db),
    current_user: models.User = Depends(get_current_user)
):
    products = db.query(models.Product).filter(models.Product.user_id == current_user.id).all()
    
    for p in products:
        if p.opened_at:
            p.expiry_date = p.opened_at + relativedelta(months=p.pao_months)
            
    return products