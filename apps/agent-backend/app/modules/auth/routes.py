from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.deps import get_current_user
from app.db.session import get_session
from app.modules.auth.models import User
from app.modules.auth.schemas import LoginRequest, RefreshRequest, TokenResponse, UserRead
from app.modules.auth.service import authenticate_user, issue_tokens, refresh_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, session: Session = Depends(get_session)) -> TokenResponse:
    user = authenticate_user(session, payload.email, payload.password)
    access_token, refresh_token = issue_tokens(user)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, session: Session = Depends(get_session)) -> TokenResponse:
    access_token, refresh_token = refresh_access_token(session, payload.refresh_token)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
