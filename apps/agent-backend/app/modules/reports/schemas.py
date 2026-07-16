from datetime import datetime

from pydantic import BaseModel

from app.modules.candidate_matching.models import CandidateMatchStatus
from app.modules.reports.models import ReportVersionSource


class ReportVersionSummary(BaseModel):
    id: int
    version_number: int
    source: ReportVersionSource
    created_by: int
    created_at: datetime


class ReportVersionRead(ReportVersionSummary):
    report_id: int
    content: str


class ReportRead(BaseModel):
    id: int
    hiring_project_id: int
    status: CandidateMatchStatus
    error_message: str | None
    current_version_id: int | None
    content: str | None
    created_at: datetime
    updated_at: datetime


class SaveVersionRequest(BaseModel):
    content: str
