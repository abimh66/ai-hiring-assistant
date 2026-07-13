from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from app.core.security import decode_token
from app.db.session import get_session
from app.modules.auth.models import User

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: Session = Depends(get_session),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(credentials.credentials)
    except Exception as exc:
        raise credentials_exception from exc

    if payload.get("type") != "access":
        raise credentials_exception

    user = session.get(User, int(payload["sub"]))
    if user is None or not user.is_active:
        raise credentials_exception
    return user
