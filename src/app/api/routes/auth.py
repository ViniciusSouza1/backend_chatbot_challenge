# src/app/api/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import BaseModel, EmailStr

from app.db.dependencies import get_db
from app.domain.models import User
from app.core.jwt import create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Se suas senhas já estiverem com hash (bcrypt), essa função verifica.
# Se ainda houver senhas em texto puro, ela também aceita em modo compatível.
def verify_password(plain_password: str, stored_password: str) -> bool:
    try:
        if stored_password and stored_password.startswith("$2"):
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            return pwd_context.verify(plain_password, stored_password)
    except Exception:
        pass
    return plain_password == stored_password


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalars(select(User).where(User.email == payload.email)).first()
    if not user or not verify_password(payload.password, user.password or ""):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token({"sub": user.id, "email": user.email})
    return {"access_token": token, "token_type": "bearer", "user": {"id": user.id, "email": user.email}}
