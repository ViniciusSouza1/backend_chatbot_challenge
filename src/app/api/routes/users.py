from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password

from app.db.dependencies import get_db
from app.domain.models import User
from app.domain.schemas import UserCreate, UserRead
from app.api.deps.permissions import require_admin

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db), current_user = Depends(require_admin)) -> list[User]:
    if(not current_user):
       raise HTTPException(status_code=status.HTTPException.UNAUTHORIZED, detail="Admin only")
    return db.scalars(select(User)).all()


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    user = User(email=payload.email, password=hash_password(payload.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered."
        )
    db.refresh(user)
    return user
