from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.modules.auth.models import User


def get_user_by_email(session: Session, email: str) -> User | None:
    return session.exec(select(User).where(User.email == email)).first()


def authenticate_user(session: Session, email: str, password: str) -> User:
    user = get_user_by_email(session, email)
    if user is None or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    return user


def issue_tokens(user: User) -> tuple[str, str]:
    subject = str(user.id)
    return create_access_token(subject), create_refresh_token(subject)


def refresh_access_token(session: Session, refresh_token: str) -> tuple[str, str]:
    try:
        payload = decode_token(refresh_token)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        ) from exc

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    user = session.get(User, int(payload["sub"]))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return issue_tokens(user)
