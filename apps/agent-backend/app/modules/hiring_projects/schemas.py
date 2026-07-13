from datetime import datetime

from pydantic import BaseModel

from app.modules.hiring_projects.models import HiringProjectStatus


class HiringProjectCreate(BaseModel):
    title: str
    job_description: str


class HiringProjectUpdate(BaseModel):
    title: str | None = None
    job_description: str | None = None
    status: HiringProjectStatus | None = None


class HiringProjectRead(BaseModel):
    id: int
    title: str
    job_description: str
    status: HiringProjectStatus
    created_by: int
    created_at: datetime
