from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.modules.auth.models import User
from app.modules.auth.schemas import UserRead


def to_user_read(user: User) -> UserRead:
    return UserRead(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_pending=user.password_hash is None,
        created_at=user.created_at,
    )


def get_user_by_email(session: Session, email: str) -> User | None:
    return session.exec(select(User).where(User.email == email)).first()


def get_user_by_invite_token(session: Session, token: str) -> User | None:
    return session.exec(select(User).where(User.invite_token == token)).first()


def authenticate_user(session: Session, email: str, password: str) -> User:
    user = get_user_by_email(session, email)
    if (
        user is None
        or user.password_hash is None
        or not user.is_active
        or not verify_password(password, user.password_hash)
    ):
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
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return issue_tokens(user)


def accept_invite(session: Session, token: str, password: str) -> User:
    user = get_user_by_invite_token(session, token)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid invite token")

    user.password_hash = hash_password(password)
    user.invite_token = None
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
