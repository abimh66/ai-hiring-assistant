from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.modules.resume_analysis.models import ResumeAnalysis, ResumeAnalysisStatus


def get_analysis_by_application_id(
    session: Session, application_id: int
) -> ResumeAnalysis | None:
    return session.exec(
        select(ResumeAnalysis).where(ResumeAnalysis.application_id == application_id)
    ).first()


def get_analysis_or_404(session: Session, application_id: int) -> ResumeAnalysis:
    analysis = get_analysis_by_application_id(session, application_id)
    if analysis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resume analysis not found"
        )
    return analysis


def get_or_create_pending_analysis(session: Session, application_id: int) -> ResumeAnalysis:
    analysis = get_analysis_by_application_id(session, application_id)
    if analysis is None:
        analysis = ResumeAnalysis(application_id=application_id)
    analysis.status = ResumeAnalysisStatus.pending
    analysis.error_message = None
    analysis.updated_at = datetime.now(timezone.utc)
    session.add(analysis)
    session.commit()
    session.refresh(analysis)
    return analysis


def mark_analysis_completed(
    session: Session,
    analysis: ResumeAnalysis,
    profile: dict,
    extraction_method: str,
    extracted_text: str,
) -> ResumeAnalysis:
    analysis.status = ResumeAnalysisStatus.completed
    analysis.summary = profile["summary"]
    analysis.skills = profile["skills"]
    analysis.experience = profile["experience"]
    analysis.education = profile["education"]
    analysis.strengths = profile["strengths"]
    analysis.concerns = profile["concerns"]
    analysis.suggested_interview_topics = profile["suggested_interview_topics"]
    analysis.extraction_method = extraction_method
    analysis.extracted_text = extracted_text
    analysis.error_message = None
    analysis.updated_at = datetime.now(timezone.utc)
    session.add(analysis)
    session.commit()
    session.refresh(analysis)
    return analysis


def mark_analysis_failed(session: Session, analysis: ResumeAnalysis, error_message: str) -> ResumeAnalysis:
    analysis.status = ResumeAnalysisStatus.failed
    analysis.error_message = error_message
    analysis.updated_at = datetime.now(timezone.utc)
    session.add(analysis)
    session.commit()
    session.refresh(analysis)
    return analysis


def mark_embedding_completed(session: Session, analysis: ResumeAnalysis) -> ResumeAnalysis:
    analysis.embedding_status = ResumeAnalysisStatus.completed
    analysis.embedding_error_message = None
    analysis.updated_at = datetime.now(timezone.utc)
    session.add(analysis)
    session.commit()
    session.refresh(analysis)
    return analysis


def mark_embedding_failed(session: Session, analysis: ResumeAnalysis, error_message: str) -> ResumeAnalysis:
    analysis.embedding_status = ResumeAnalysisStatus.failed
    analysis.embedding_error_message = error_message
    analysis.updated_at = datetime.now(timezone.utc)
    session.add(analysis)
    session.commit()
    session.refresh(analysis)
    return analysis


def reset_embedding_to_pending(session: Session, analysis: ResumeAnalysis) -> ResumeAnalysis:
    analysis.embedding_status = ResumeAnalysisStatus.pending
    analysis.embedding_error_message = None
    analysis.updated_at = datetime.now(timezone.utc)
    session.add(analysis)
    session.commit()
    session.refresh(analysis)
    return analysis
