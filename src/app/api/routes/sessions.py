from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.domain.models import Session as SessionModel
from app.domain.models import User
from app.domain.schemas import SessionCreate, SessionRead

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.get("", response_model=list[SessionRead])
def list_sessions(db: Session = Depends(get_db)) -> list[SessionModel]:
    return db.scalars(select(SessionModel)).all()


@router.get("/by-user/{user_id}", response_model=list[SessionRead])
def list_sessions_by_user(user_id: str, db: Session = Depends(get_db)) -> list[SessionModel]:
    return db.scalars(select(SessionModel).where(SessionModel.user_id == user_id)).all()


@router.post("", response_model=SessionRead, status_code=status.HTTP_201_CREATED)
def create_session(
    payload: SessionCreate = Body(default=None),  # ✅ torna o corpo opcional
    db: Session = Depends(get_db),
) -> SessionModel:
    # No body, create session for guest
    if payload is None:
        payload = SessionCreate(user_id=None, title=None)

    # user_id optional
    raw_uid = payload.user_id
    uid = (raw_uid.strip() if isinstance(raw_uid, str) else raw_uid) or None

    # Validate user if provided
    if uid is not None:
        user = db.get(User, uid)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
            )

    session = SessionModel(user_id=uid, title=(payload.title or None))
    db.add(session)
    db.commit()
    db.refresh(session)
    return session
