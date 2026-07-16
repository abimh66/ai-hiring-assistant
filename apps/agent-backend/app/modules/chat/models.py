from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import JSON, Column, Text
from sqlmodel import Field, SQLModel


class ChatRole(str, Enum):
    user = "user"
    assistant = "assistant"


class ChatConversation(SQLModel, table=True):
    __tablename__ = "chat_conversations"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    hiring_project_id: int | None = Field(default=None, foreign_key="hiring_projects.id")
    title: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChatMessage(SQLModel, table=True):
    __tablename__ = "chat_messages"

    id: int | None = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="chat_conversations.id", index=True)
    role: ChatRole
    content: str = Field(sa_column=Column(Text))
    activity: list[dict] | None = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
