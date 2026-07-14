from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import JSON, Column, Text
from sqlmodel import Field, SQLModel


class ResumeAnalysisStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


class ResumeAnalysis(SQLModel, table=True):
    __tablename__ = "resume_analyses"

    id: int | None = Field(default=None, primary_key=True)
    application_id: int = Field(foreign_key="applications.id", unique=True)
    status: ResumeAnalysisStatus = Field(default=ResumeAnalysisStatus.pending)

    summary: str | None = None
    skills: list[str] | None = Field(default=None, sa_column=Column(JSON))
    experience: list[dict] | None = Field(default=None, sa_column=Column(JSON))
    education: list[dict] | None = Field(default=None, sa_column=Column(JSON))
    strengths: list[str] | None = Field(default=None, sa_column=Column(JSON))
    concerns: list[str] | None = Field(default=None, sa_column=Column(JSON))
    suggested_interview_topics: list[str] | None = Field(default=None, sa_column=Column(JSON))

    extraction_method: str | None = None
    error_message: str | None = None
    extracted_text: str | None = Field(default=None, sa_column=Column(Text))

    embedding_status: ResumeAnalysisStatus = Field(default=ResumeAnalysisStatus.pending)
    embedding_error_message: str | None = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
