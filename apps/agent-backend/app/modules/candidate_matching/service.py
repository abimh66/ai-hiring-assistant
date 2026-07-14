from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.modules.candidate_matching.models import CandidateMatch, CandidateMatchStatus


def get_match_by_application_id(session: Session, application_id: int) -> CandidateMatch | None:
    return session.exec(
        select(CandidateMatch).where(CandidateMatch.application_id == application_id)
    ).first()


def get_match_or_404(session: Session, application_id: int) -> CandidateMatch:
    match = get_match_by_application_id(session, application_id)
    if match is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate match not found")
    return match


def get_or_create_pending_match(session: Session, application_id: int) -> CandidateMatch:
    match = get_match_by_application_id(session, application_id)
    if match is None:
        match = CandidateMatch(application_id=application_id)
    match.status = CandidateMatchStatus.pending
    match.error_message = None
    match.updated_at = datetime.now(timezone.utc)
    session.add(match)
    session.commit()
    session.refresh(match)
    return match


def mark_match_completed(session: Session, match: CandidateMatch, result: dict) -> CandidateMatch:
    match.status = CandidateMatchStatus.completed
    match.match_score = result["match_score"]
    match.strengths = result["strengths"]
    match.weaknesses = result["weaknesses"]
    match.missing_skills = result["missing_skills"]
    match.reasoning = result["reasoning"]
    match.error_message = None
    match.updated_at = datetime.now(timezone.utc)
    session.add(match)
    session.commit()
    session.refresh(match)
    return match


def mark_match_failed(session: Session, match: CandidateMatch, error_message: str) -> CandidateMatch:
    match.status = CandidateMatchStatus.failed
    match.error_message = error_message
    match.updated_at = datetime.now(timezone.utc)
    session.add(match)
    session.commit()
    session.refresh(match)
    return match
