from itertools import combinations
from ...core.skincare_logic import check_compatibility
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from ...database import models, session
from ...schemas import routine as routine_schema
from .auth import get_current_user
from typing import List

router = APIRouter(prefix="/routines", tags=["Routines"])

@router.post("/insert", response_model=routine_schema.RoutineOut)
def create_routine_header(
    routine_in: routine_schema.RoutineCreate,
    db: Session = Depends(session.get_db),
    current_user: models.User = Depends(get_current_user)
):
    existing = db.query(models.Routine).filter(
        models.Routine.user_id == current_user.id,
        models.Routine.routine_type == routine_in.routine_type
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail=f"Routine {routine_in.routine_type} sudah ada")

    new_routine = models.Routine(
        user_id=current_user.id,
        routine_type=routine_in.routine_type,
        scheduled_time=routine_in.scheduled_time
    )
    db.add(new_routine)
    db.commit()
    db.refresh(new_routine)
    return new_routine

@router.post("/add-item/{routine_id}")
def add_item_to_routine(
    routine_id: int,
    item_in: routine_schema.RoutineItemBase,
    db: Session = Depends(session.get_db),
    current_user: models.User = Depends(get_current_user)
):
    routine = db.query(models.Routine).filter(
        models.Routine.id == routine_id, 
        models.Routine.user_id == current_user.id
    ).first()
    if not routine:
        raise HTTPException(status_code=404, detail="Routine tidak ditemukan")

    new_item = models.RoutineItem(
        routine_id=routine_id,
        product_id=item_in.product_id,
        order_index=item_in.order_index
    )
    db.add(new_item)
    db.commit()
    return {"message": "Produk berhasil ditambahkan ke routine"}

@router.get("/browse", response_model=List[routine_schema.RoutineOut])
def get_my_routines(
    db: Session = Depends(session.get_db),
    current_user: models.User = Depends(get_current_user)
):
    routines = db.query(models.Routine).options(
        joinedload(models.Routine.items).joinedload(models.RoutineItem.product)
    ).filter(models.Routine.user_id == current_user.id).all()

    for r in routines:
        product_ids = [item.product_id for item in r.items]
        r.can_combine = True
        r.conflicts = []
        r.advice = None

        if len(r.items) > 1:
            all_ingredients = [
                (item.product.id, [i.name for i in item.product.ingredients]) 
                for item in r.items
            ]

            conflicts_found = []

            product_pairs = combinations(all_ingredients, 2)

            for (prod_id_a, ings_a), (prod_id_b, ings_b) in product_pairs:
                for ing_a in ings_a:
                    for ing_b in ings_b:
                        is_safe, message = check_compatibility(ing_a, ing_b)
                        if not is_safe:
                            conflicts_found.append(message)
            
            if conflicts_found:
                r.can_combine = False
                r.conflicts = list(set(conflicts_found))
                r.advice = "Gunakan di waktu berbeda (misal: satu pagi, satu malam)."


    return routines