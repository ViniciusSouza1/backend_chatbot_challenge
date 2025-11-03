# src/app/api/routes/sessions.py
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Optional

from app.db.dependencies import get_db
from app.domain.models import Session as SessionModel, User
from app.domain.schemas import SessionCreate, SessionRead, ClaimSessionsRequest, ClaimSessionsResponse
from app.api.deps.auth import get_current_user, get_current_user_optional
from app.core.config import settings

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

def _is_admin(user: Optional[User]) -> bool:
    if not user:
        return False
    admins = {a.strip().lower() for a in (settings.admin_emails or []) if a.strip()}
    return user.email.lower() in admins

@router.get("", response_model=list[SessionRead])
def list_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # admin-only em outro lugar, se preferir troque por require_admin
) -> list[SessionModel]:
    # Se você já tem require_admin, use-o aqui:
    # from app.api.deps.permissions import require_admin
    # def list_sessions(db: Session = Depends(get_db), _: User = Depends(require_admin)) -> list[SessionModel]:
    return db.scalars(select(SessionModel)).all()

@router.get("/by-user/{user_id}", response_model=list[SessionRead])
def list_sessions_by_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SessionModel]:
    # dono ou admin
    if current_user.id != user_id and not _is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return db.scalars(select(SessionModel).where(SessionModel.user_id == user_id)).all()

@router.post("", response_model=SessionRead, status_code=status.HTTP_201_CREATED)
def create_session(
    payload: Optional[SessionCreate] = Body(default=None),           # body opcional
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> SessionModel:
    data = payload or SessionCreate(user_id=None, title=None)

    # Se vier user_id, precisa ser o próprio (ou admin)
    if data.user_id is not None:
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
        if current_user.id != data.user_id and not _is_admin(current_user):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

        # também valide a existência do usuário
        user = db.get(User, data.user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    # Cria sessão (anônima se user_id=None)
    sess = SessionModel(user_id=data.user_id, title=(data.title or None))
    db.add(sess)
    db.commit()
    db.refresh(sess)
    return sess

@router.post("/claim", response_model=ClaimSessionsResponse, status_code=status.HTTP_200_OK)
def claim_sessions(
    payload: ClaimSessionsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # usuário precisa estar autenticado agora
):
    """
    Vincula as sessões anônimas (user_id=None) passadas em sessionIds ao usuário autenticado.
    - Se a sessão já é do próprio usuário, conta em `already_owned_by_user`.
    - Se a sessão tem outro dono, conta em `owned_by_another_user`.
    - Se não encontrada, conta em `not_found`.
    - Se anônima, atualiza para o current_user.id (conta em `claimed`).
    Idempotente: chamar novamente não duplica efeitos.
    """
    seen = set()
    claimed = 0
    already_owned_by_user = 0
    owned_by_another_user = 0
    not_found = 0
    details = []

    for sid in payload.sessionIds:
        if not sid or sid in seen:
            continue
        seen.add(sid)

        sess = db.get(SessionModel, sid)
        if not sess:
            not_found += 1
            details.append({"sessionId": sid, "status": "not_found"})
            continue

        # Já é do próprio user?
        if sess.user_id == current_user.id:
            already_owned_by_user += 1
            details.append({"sessionId": sid, "status": "already_owned_by_user"})
            continue

        # É anônima? (pode reivindicar)
        if sess.user_id is None:
            sess.user_id = current_user.id
            db.add(sess)
            claimed += 1
            details.append({"sessionId": sid, "status": "claimed"})
            continue

        # Tem outro dono -> não pode
        owned_by_another_user += 1
        details.append({"sessionId": sid, "status": "owned_by_another_user"})

    if claimed > 0:
        db.commit()

    total = len(seen)
    return ClaimSessionsResponse(
        claimed=claimed,
        already_owned_by_user=already_owned_by_user,
        owned_by_another_user=owned_by_another_user,
        not_found=not_found,
        processed=total,
        details=details,
    )