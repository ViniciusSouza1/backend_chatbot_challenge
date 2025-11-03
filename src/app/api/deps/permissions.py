# src/app/api/deps/permissions.py
from fastapi import Depends, HTTPException, Request, status
from app.domain.models import User
from app.api.deps.auth import get_current_user

# --- ACCESS LEVELS ---

def require_user(request: Request) -> User:
    """
    Requires the middleware to have authenticated the user.
    Used in routes that require normal login.
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return user


def require_admin(user: User = Depends(require_user)) -> User:
    """
    Requires that the authenticated user is on the admins list (config.env).    """
    from app.core.config import settings
    admins = {a.strip().lower() for a in (settings.admin_emails or []) if a.strip()}
    if user.email.lower() not in admins:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return user


def optional_user(request: Request):
    """
    Returns the authenticated user if present, otherwise None.
    Used in public routes that benefit from knowing who is logged in.
    """
    return getattr(request.state, "user", None)
