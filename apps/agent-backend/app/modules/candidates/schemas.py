from datetime import datetime

from pydantic import BaseModel, EmailStr


class CandidateRead(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: str | None
    created_at: datetime
