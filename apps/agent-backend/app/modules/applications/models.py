from datetime import datetime, timezone
from enum import Enum

from sqlmodel import Field, SQLModel


class ApplicationStatus(str, Enum):
    new = "new"
    reviewing = "reviewing"
    rejected = "rejected"
    shortlisted = "shortlisted"


class Application(SQLModel, table=True):
    __tablename__ = "applications"

    id: int | None = Field(default=None, primary_key=True)
    candidate_id: int = Field(foreign_key="candidates.id")
    hiring_project_id: int = Field(foreign_key="hiring_projects.id")
    resume_file_key: str
    interview_notes_file_key: str | None = None
    status: ApplicationStatus = Field(default=ApplicationStatus.new)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
