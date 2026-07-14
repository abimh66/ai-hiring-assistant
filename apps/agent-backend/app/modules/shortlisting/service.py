from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.modules.candidate_matching.models import CandidateMatchStatus
from app.modules.shortlisting.models import ShortlistRecommendation


def get_shortlist_by_project_id(session: Session, hiring_project_id: int) -> ShortlistRecommendation | None:
    return session.exec(
        select(ShortlistRecommendation).where(
            ShortlistRecommendation.hiring_project_id == hiring_project_id
        )
    ).first()


def get_shortlist_or_404(session: Session, hiring_project_id: int) -> ShortlistRecommendation:
    shortlist = get_shortlist_by_project_id(session, hiring_project_id)
    if shortlist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Shortlist recommendation not found"
        )
    return shortlist


def get_or_create_pending_shortlist(session: Session, hiring_project_id: int) -> ShortlistRecommendation:
    shortlist = get_shortlist_by_project_id(session, hiring_project_id)
    if shortlist is None:
        shortlist = ShortlistRecommendation(hiring_project_id=hiring_project_id)
    shortlist.status = CandidateMatchStatus.pending
    shortlist.error_message = None
    shortlist.updated_at = datetime.now(timezone.utc)
    session.add(shortlist)
    session.commit()
    session.refresh(shortlist)
    return shortlist


def mark_shortlist_completed(
    session: Session,
    shortlist: ShortlistRecommendation,
    recommendations: list[dict],
    overall_summary: str,
) -> ShortlistRecommendation:
    shortlist.status = CandidateMatchStatus.completed
    shortlist.recommendations = recommendations
    shortlist.overall_summary = overall_summary
    shortlist.error_message = None
    shortlist.updated_at = datetime.now(timezone.utc)
    session.add(shortlist)
    session.commit()
    session.refresh(shortlist)
    return shortlist


def mark_shortlist_failed(
    session: Session, shortlist: ShortlistRecommendation, error_message: str
) -> ShortlistRecommendation:
    shortlist.status = CandidateMatchStatus.failed
    shortlist.error_message = error_message
    shortlist.updated_at = datetime.now(timezone.utc)
    session.add(shortlist)
    session.commit()
    session.refresh(shortlist)
    return shortlist
