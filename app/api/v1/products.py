from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from ...database import models, session
from ...schemas import product as product_schema
from .auth import get_current_user
from ...schemas import routine as routine_schema
from ...core.skincare_logic import check_compatibility

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/insert", response_model=product_schema.ProductOut)
def create_product(
    product_in: product_schema.ProductCreate, 
    db: Session = Depends(session.get_db),
    current_user: models.User = Depends(get_current_user)
):
    ing_ids = product_in.ingredient_ids
    
    product_data = product_in.model_dump()
    product_data.pop("ingredient_ids", None)
    
    new_product = models.Product(**product_data, user_id=current_user.id)
    
    if ing_ids:
        active_ings = db.query(models.ActiveIngredient).filter(models.ActiveIngredient.id.in_(ing_ids)).all()
        new_product.ingredients = active_ings
    
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

@router.get("/active-ingredients/browse", response_model=List[product_schema.IngredientOut])
def get_active_ingredients(db: Session = Depends(session.get_db)):
    """
    Mengambil semua daftar bahan aktif dari database untuk pilihan dropdown di Frontend.
    """
    ingredients = db.query(models.ActiveIngredient).all()
    return ingredients

@router.post("/check-conflict")
def check_product_conflict(
    req: routine_schema.ConflictCheckRequest,
    db: Session = Depends(session.get_db)
):
    # 1. Ambil data kedua produk beserta ingredients-nya
    prod_a = db.query(models.Product).filter(models.Product.id == req.product_id_a).first()
    prod_b = db.query(models.Product).filter(models.Product.id == req.product_id_b).first()

    if not prod_a or not prod_b:
        raise HTTPException(status_code=404, detail="Produk tidak ditemukan")

    # 2. Ambil list nama bahan aktif dari masing-masing produk
    ing_a = [i.name for i in prod_a.ingredients]
    ing_b = [i.name for i in prod_b.ingredients]

    # 3. Logika Tabrakan (Bisa dikembangkan lebih lanjut)
    conflicts_found = []
    
    # Contoh logic: Retinol vs AHA/BHA/Vit C
    for a in ing_a:
        for b in ing_b:
            is_safe, message = check_compatibility(a, b) # Pakai fungsi utils kita tadi
            if not is_safe:
                conflicts_found.append(message)

    if conflicts_found:
        return {
            "can_combine": False,
            "conflicts": conflicts_found,
            "advice": "Gunakan di waktu berbeda (misal: satu pagi, satu malam)."
        }

    return {
        "can_combine": True,
        "conflicts": [],
        "advice": "Aman digunakan bersamaan!"
    }