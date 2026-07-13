from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str | None = None
    full_name: str
    is_active: bool = Field(default=True)
    invite_token: str | None = Field(default=None, unique=True, index=True)
    invited_by: int | None = Field(default=None, foreign_key="users.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
