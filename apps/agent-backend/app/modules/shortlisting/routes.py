from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.deps import get_current_user
from app.db.session import get_session
from app.modules.hiring_projects.service import get_hiring_project_or_404
from app.modules.shortlisting.schemas import ShortlistRecommendationRead
from app.modules.shortlisting.service import get_or_create_pending_shortlist, get_shortlist_or_404
from app.worker.tasks import generate_shortlist

router = APIRouter(
    prefix="/hiring-projects/{hiring_project_id}/shortlist",
    tags=["shortlisting"],
    dependencies=[Depends(get_current_user)],
)


@router.post("", response_model=ShortlistRecommendationRead)
def trigger_shortlist(hiring_project_id: int, session: Session = Depends(get_session)):
    get_hiring_project_or_404(session, hiring_project_id)
    shortlist = get_or_create_pending_shortlist(session, hiring_project_id)
    generate_shortlist.delay(hiring_project_id)
    return shortlist


@router.get("", response_model=ShortlistRecommendationRead)
def read_shortlist(hiring_project_id: int, session: Session = Depends(get_session)):
    get_hiring_project_or_404(session, hiring_project_id)
    return get_shortlist_or_404(session, hiring_project_id)
