from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.core.deps import get_current_user
from app.db.session import get_session
from app.modules.applications.service import get_application_or_404
from app.modules.resume_analysis.models import ResumeAnalysisStatus
from app.modules.resume_analysis.schemas import ResumeAnalysisRead
from app.modules.resume_analysis.service import (
    get_analysis_or_404,
    get_or_create_pending_analysis,
    reset_embedding_to_pending,
)
from app.worker.tasks import analyze_resume, embed_resume

router = APIRouter(
    prefix="/applications/{application_id}/resume-analysis",
    tags=["resume-analysis"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=ResumeAnalysisRead)
def get_resume_analysis(application_id: int, session: Session = Depends(get_session)):
    get_application_or_404(session, application_id)
    return get_analysis_or_404(session, application_id)


@router.post("/retry", response_model=ResumeAnalysisRead)
def retry_resume_analysis(application_id: int, session: Session = Depends(get_session)):
    get_application_or_404(session, application_id)
    analysis = get_or_create_pending_analysis(session, application_id)
    analyze_resume.delay(application_id)
    return analysis


@router.post("/retry-embedding", response_model=ResumeAnalysisRead)
def retry_resume_embedding(application_id: int, session: Session = Depends(get_session)):
    get_application_or_404(session, application_id)
    analysis = get_analysis_or_404(session, application_id)
    if analysis.status != ResumeAnalysisStatus.completed or analysis.extracted_text is None:
        raise HTTPException(
            status_code=409,
            detail="Resume analysis must be completed with extracted text before retrying embedding",
        )
    analysis = reset_embedding_to_pending(session, analysis)
    embed_resume.delay(application_id)
    return analysis
