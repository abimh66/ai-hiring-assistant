from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.deps import get_current_user
from app.db.session import get_session
from app.modules.applications.schemas import ApplicationRead
from app.modules.applications.service import list_applications_for_candidate
from app.modules.candidates.schemas import CandidateRead
from app.modules.candidates.service import get_candidate_or_404

router = APIRouter(prefix="/candidates", tags=["candidates"], dependencies=[Depends(get_current_user)])


@router.get("/{candidate_id}", response_model=CandidateRead)
def get_candidate(candidate_id: int, session: Session = Depends(get_session)):
    return get_candidate_or_404(session, candidate_id)


@router.get("/{candidate_id}/applications", response_model=list[ApplicationRead])
def get_candidate_applications(candidate_id: int, session: Session = Depends(get_session)):
    get_candidate_or_404(session, candidate_id)
    return list_applications_for_candidate(session, candidate_id)
