from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

from ...database.session import get_db
from ...database import models
from ...core import security
from ...schemas import user as user_schema

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=user_schema.UserOut)
def register(user_in: user_schema.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")

    hashed_pwd = security.hash_password(user_in.password)
    
    new_user = models.User(
        email=user_in.email,
        password_hash=hashed_pwd,
        full_name=user_in.full_name,
        alias=user_in.alias,
        date_of_birth=user_in.date_of_birth,
        gender=user_in.gender,
        skin_type=user_in.skin_type
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=user_schema.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password salah",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    from ...core.utils import calculate_age
    user_age = calculate_age(user.date_of_birth)

    token_data = {
        "sub": user.email,
        "full_name": user.full_name,
        "alias": user.alias,
        "gender": user.gender,
        "date_of_birth": str(user.date_of_birth) if user.date_of_birth else None,
        "age": user_age,
        "skin_type": user.skin_type
    }
    
    access_token = security.create_access_token(data=token_data)
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user