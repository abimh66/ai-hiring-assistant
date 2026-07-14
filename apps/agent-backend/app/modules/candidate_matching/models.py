from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import JSON, Column, Text
from sqlmodel import Field, SQLModel


class CandidateMatchStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


class CandidateMatch(SQLModel, table=True):
    __tablename__ = "candidate_matches"

    id: int | None = Field(default=None, primary_key=True)
    application_id: int = Field(foreign_key="applications.id", unique=True)
    status: CandidateMatchStatus = Field(default=CandidateMatchStatus.pending)

    match_score: int | None = None
    strengths: list[str] | None = Field(default=None, sa_column=Column(JSON))
    weaknesses: list[str] | None = Field(default=None, sa_column=Column(JSON))
    missing_skills: list[str] | None = Field(default=None, sa_column=Column(JSON))
    reasoning: str | None = Field(default=None, sa_column=Column(Text))

    error_message: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
