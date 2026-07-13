from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.deps import get_current_user
from app.db.session import get_session
from app.modules.auth.models import User
from app.modules.auth.schemas import UserRead
from app.modules.auth.service import to_user_read
from app.modules.users.schemas import InviteUserRequest, InviteUserResponse
from app.modules.users.service import deactivate_user, get_user_or_404, invite_user, list_users

router = APIRouter(prefix="/users", tags=["users"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[UserRead])
def list_users_route(session: Session = Depends(get_session)):
    return [to_user_read(user) for user in list_users(session)]


@router.post("/invite", response_model=InviteUserResponse, status_code=201)
def invite_user_route(
    payload: InviteUserRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    user, invite_token = invite_user(session, payload, invited_by=current_user.id)
    return InviteUserResponse(user=to_user_read(user), invite_token=invite_token)


@router.delete("/{user_id}", response_model=UserRead)
def deactivate_user_route(user_id: int, session: Session = Depends(get_session)):
    user = get_user_or_404(session, user_id)
    return to_user_read(deactivate_user(session, user))
