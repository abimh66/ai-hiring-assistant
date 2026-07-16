from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel


class ApplicationStatus(str, Enum):
    new = "new"
    reviewing = "reviewing"
    rejected = "rejected"
    shortlisted = "shortlisted"


class Application(SQLModel, table=True):
    __tablename__ = "applications"

    id: int | None = Field(default=None, primary_key=True)
    candidate_id: int | None = Field(default=None, foreign_key="candidates.id")
    hiring_project_id: int = Field(foreign_key="hiring_projects.id")
    resume_file_key: str
    resume_original_filename: str
    interview_notes_file_key: str | None = None
    interview_notes_text: str | None = Field(default=None, sa_column=Column(Text))
    status: ApplicationStatus = Field(default=ApplicationStatus.new)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
