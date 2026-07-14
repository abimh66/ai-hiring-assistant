from datetime import datetime

from pydantic import BaseModel

from app.modules.applications.models import ApplicationStatus


class ApplicationUpdate(BaseModel):
    status: ApplicationStatus | None = None


class ApplicationRead(BaseModel):
    id: int
    candidate_id: int | None
    hiring_project_id: int
    resume_file_key: str
    resume_original_filename: str
    interview_notes_file_key: str | None
    status: ApplicationStatus
    created_at: datetime


class ApplicationUploadResult(BaseModel):
    filename: str
    application: ApplicationRead | None = None
    error: str | None = None
