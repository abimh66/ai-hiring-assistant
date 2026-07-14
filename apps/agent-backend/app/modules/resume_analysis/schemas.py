from datetime import datetime

from pydantic import BaseModel

from app.modules.resume_analysis.models import ResumeAnalysisStatus


class ResumeAnalysisRead(BaseModel):
    id: int
    application_id: int
    status: ResumeAnalysisStatus
    summary: str | None
    skills: list[str] | None
    experience: list[dict] | None
    education: list[dict] | None
    strengths: list[str] | None
    concerns: list[str] | None
    suggested_interview_topics: list[str] | None
    extraction_method: str | None
    error_message: str | None
    embedding_status: ResumeAnalysisStatus
    embedding_error_message: str | None
    created_at: datetime
    updated_at: datetime
