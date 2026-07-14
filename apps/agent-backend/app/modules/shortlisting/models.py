from datetime import datetime, timezone

from sqlalchemy import JSON, Column, Text
from sqlmodel import Field, SQLModel

from app.modules.candidate_matching.models import CandidateMatchStatus


class ShortlistRecommendation(SQLModel, table=True):
    __tablename__ = "shortlist_recommendations"

    id: int | None = Field(default=None, primary_key=True)
    hiring_project_id: int = Field(foreign_key="hiring_projects.id", unique=True)
    status: CandidateMatchStatus = Field(default=CandidateMatchStatus.pending)

    recommendations: list[dict] | None = Field(default=None, sa_column=Column(JSON))
    overall_summary: str | None = Field(default=None, sa_column=Column(Text))

    error_message: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
