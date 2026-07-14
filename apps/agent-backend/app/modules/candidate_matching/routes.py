from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.deps import get_current_user
from app.db.session import get_session
from app.modules.applications.service import get_application_or_404
from app.modules.candidate_matching.schemas import CandidateMatchRead
from app.modules.candidate_matching.service import get_match_or_404, get_or_create_pending_match
from app.worker.tasks import match_candidate

router = APIRouter(
    prefix="/applications/{application_id}/match",
    tags=["candidate-matching"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=CandidateMatchRead)
def get_candidate_match(application_id: int, session: Session = Depends(get_session)):
    get_application_or_404(session, application_id)
    return get_match_or_404(session, application_id)


@router.post("/retry", response_model=CandidateMatchRead)
def retry_candidate_match(application_id: int, session: Session = Depends(get_session)):
    get_application_or_404(session, application_id)
    match = get_or_create_pending_match(session, application_id)
    match_candidate.delay(application_id)
    return match
