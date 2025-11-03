# src/app/api/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import BaseModel, EmailStr

from app.db.dependencies import get_db
from app.domain.models import User
from app.domain.schemas import UserPublic
from app.core.jwt import create_access_token
from app.core.security import hash_password, verify_password as verify_hash
from app.api.deps.permissions import require_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic

@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalars(select(User).where(User.email == payload.email)).first()

    def _matches(plain, stored):
        if not stored:
            return False
        if "$" in stored:
            return verify_hash(plain, stored)
        return plain == stored

    if not user or not _matches(payload.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = create_access_token({"sub": user.id})
    return LoginResponse(access_token=token, user=UserPublic(id=user.id, email=user.email))

@router.get("/me", response_model=UserPublic)
def me(current_user: User = Depends(require_user)):
    return UserPublic(id=current_user.id, email=current_user.email)

@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.scalars(select(User).where(User.email == payload.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered.")
    user = User(email=payload.email, password=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserPublic(id=user.id, email=user.email)