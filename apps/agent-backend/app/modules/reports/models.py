from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel

from app.modules.candidate_matching.models import CandidateMatchStatus


class ReportVersionSource(str, Enum):
    ai_generated = "ai_generated"
    edited = "edited"
    restored = "restored"


class HiringReport(SQLModel, table=True):
    __tablename__ = "hiring_reports"

    id: int | None = Field(default=None, primary_key=True)
    hiring_project_id: int = Field(foreign_key="hiring_projects.id", unique=True)
    status: CandidateMatchStatus = Field(default=CandidateMatchStatus.pending)
    error_message: str | None = None
    # Plain pointer, NOT a DB foreign key: a real FK here would create a cycle with
    # report_versions.report_id and break Alembic's CREATE TABLE ordering. App-level only.
    current_version_id: int | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ReportVersion(SQLModel, table=True):
    __tablename__ = "report_versions"

    id: int | None = Field(default=None, primary_key=True)
    report_id: int = Field(foreign_key="hiring_reports.id")
    version_number: int
    content: str = Field(sa_column=Column(Text))
    source: ReportVersionSource
    created_by: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
