# src/app/core/middleware/auth_context.py
from typing import Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import select
import jwt

from app.core.config import settings
from app.db.session import SessionLocal
from app.domain.models import User
from app.core.jwt import decode_access_token

class AuthContextMiddleware(BaseHTTPMiddleware):
    """
    - If there is Authorization: Bearer <token>, validate and load the user.
    - Do NOT throw an error here. Authorization is handled by dependencies (route by route).
    - Leave in request.state:
    - user: Optional[User]
    - jwt_payload: Optional[dict]
    - auth_error: Optional[str] (for observational logs)
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        request.state.user = None
        request.state.jwt_payload = None
        request.state.auth_error = None

        auth_header: str = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()
            db: Optional[Session] = None
            try:
                payload = decode_access_token(
                    token,
                    secret=settings.jwt_secret,
                    algorithms=[settings.jwt_algorithm],
                )
                user_id = payload.get("sub")
                if user_id:
                    # carrega usuário rapidamente
                    db = SessionLocal()
                    user = db.scalars(select(User).where(User.id == user_id)).first()
                    if user:
                        request.state.user = user
                        request.state.jwt_payload = payload
                    else:
                        request.state.auth_error = "user_not_found"
                else:
                    request.state.auth_error = "missing_sub"
            except jwt.ExpiredSignatureError:
                request.state.auth_error = "token_expired"
            except jwt.InvalidTokenError:
                request.state.auth_error = "invalid_token"
            except Exception as e:
                request.state.auth_error = f"unexpected:{e}"
            finally:
                if db:
                    db.close()

        response = await call_next(request)
        return response
