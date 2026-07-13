from datetime import datetime

from pydantic import BaseModel

from app.modules.applications.models import ApplicationStatus


class ApplicationCreate(BaseModel):
    candidate_email: str
    candidate_full_name: str
    candidate_phone: str | None = None


class ApplicationUpdate(BaseModel):
    status: ApplicationStatus | None = None


class ApplicationRead(BaseModel):
    id: int
    candidate_id: int
    hiring_project_id: int
    resume_file_key: str
    interview_notes_file_key: str | None
    status: ApplicationStatus
    created_at: datetime
