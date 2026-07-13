from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.modules.candidates.models import Candidate


def get_candidate_or_404(session: Session, candidate_id: int) -> Candidate:
    candidate = session.get(Candidate, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
    return candidate


def get_or_create_candidate(session: Session, email: str, full_name: str, phone: str | None) -> Candidate:
    candidate = session.exec(select(Candidate).where(Candidate.email == email)).first()
    if candidate is not None:
        return candidate

    candidate = Candidate(full_name=full_name, email=email, phone=phone)
    session.add(candidate)
    session.commit()
    session.refresh(candidate)
    return candidate
