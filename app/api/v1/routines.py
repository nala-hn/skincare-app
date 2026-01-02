from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from ...database import models, session
from ...schemas import routine as routine_schema
from .auth import get_current_user

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
    return db.query(models.Routine).options(
        joinedload(models.Routine.items)
    ).filter(models.Routine.user_id == current_user.id).all()