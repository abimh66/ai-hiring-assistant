from datetime import datetime

from pydantic import BaseModel

from app.modules.candidate_matching.models import CandidateMatchStatus


class ShortlistEntryRead(BaseModel):
    application_id: int
    rank: int
    match_score: int
    recommendation_reasoning: str
    risks: list[str]


class ShortlistRecommendationRead(BaseModel):
    id: int
    hiring_project_id: int
    status: CandidateMatchStatus
    recommendations: list[ShortlistEntryRead] | None
    overall_summary: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime
