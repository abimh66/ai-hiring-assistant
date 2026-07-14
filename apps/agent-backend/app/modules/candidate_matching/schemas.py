from datetime import datetime

from pydantic import BaseModel

from app.modules.candidate_matching.models import CandidateMatchStatus


class CandidateMatchRead(BaseModel):
    id: int
    application_id: int
    status: CandidateMatchStatus
    match_score: int | None
    strengths: list[str] | None
    weaknesses: list[str] | None
    missing_skills: list[str] | None
    reasoning: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime
