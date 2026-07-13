from datetime import datetime, timezone
from enum import Enum

from sqlmodel import Field, SQLModel


class HiringProjectStatus(str, Enum):
    open = "open"
    closed = "closed"


class HiringProject(SQLModel, table=True):
    __tablename__ = "hiring_projects"

    id: int | None = Field(default=None, primary_key=True)
    title: str
    job_description: str
    status: HiringProjectStatus = Field(default=HiringProjectStatus.open)
    created_by: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
