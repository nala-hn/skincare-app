from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from ...database.session import get_db
from ...database import models
from ...core import security
from ...schemas import user as user_schema

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=user_schema.UserOut)
def register(user_in: user_schema.UserCreate, db: Session = Depends(get_db)):
    # 1. Cek apakah email sudah terdaftar
    db_user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")
    
    # 2. Hash password dan simpan user baru
    hashed_pwd = security.hash_password(user_in.password)
    new_user = models.User(
        email=user_in.email,
        password_hash=hashed_pwd,
        skin_type=user_in.skin_type
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=user_schema.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 1. Cari user berdasarkan email (username di OAuth2)
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    # 2. Verifikasi password
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password salah",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Buat Token
    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}