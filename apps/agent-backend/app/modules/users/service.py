import secrets

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.modules.auth.models import User
from app.modules.auth.service import get_user_by_email
from app.modules.users.schemas import InviteUserRequest


def list_users(session: Session) -> list[User]:
    return list(session.exec(select(User)).all())


def get_user_or_404(session: Session, user_id: int) -> User:
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def invite_user(session: Session, payload: InviteUserRequest, invited_by: int) -> tuple[User, str]:
    if get_user_by_email(session, payload.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="A user with this email already exists"
        )

    invite_token = secrets.token_urlsafe(32)
    user = User(
        email=payload.email,
        full_name=payload.full_name,
        invite_token=invite_token,
        invited_by=invited_by,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user, invite_token


def deactivate_user(session: Session, user: User) -> User:
    user.is_active = False
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
