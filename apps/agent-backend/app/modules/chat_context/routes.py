from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.deps import get_current_user
from app.db.session import get_session
from app.modules.auth.models import User
from app.modules.chat_context.schemas import CandidateContext, MatchContext, ShortlistContext
from app.modules.chat_context.service import (
    get_candidate_context,
    get_match_context,
    get_shortlist_context,
    list_candidate_contexts,
)

router = APIRouter(prefix="/chat-context", tags=["chat-context"])


@router.get("/candidates", response_model=list[CandidateContext])
def list_candidates(
    hiring_project_id: int | None = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return list_candidate_contexts(session, current_user.id, hiring_project_id)


@router.get("/candidates/{application_id}", response_model=CandidateContext)
def get_candidate(
    application_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return get_candidate_context(session, current_user.id, application_id)


@router.get("/matches/{application_id}", response_model=MatchContext)
def get_match(
    application_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return get_match_context(session, current_user.id, application_id)


@router.get("/shortlist/{hiring_project_id}", response_model=ShortlistContext)
def get_shortlist(
    hiring_project_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return get_shortlist_context(session, current_user.id, hiring_project_id)
