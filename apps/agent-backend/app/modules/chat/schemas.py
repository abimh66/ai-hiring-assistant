from datetime import datetime

from pydantic import BaseModel

from app.modules.chat.models import ChatRole


class ChatSendRequest(BaseModel):
    message: str
    conversation_id: int | None = None
    hiring_project_id: int | None = None


class ChatMessageRead(BaseModel):
    id: int
    role: ChatRole
    content: str
    activity: list[dict] | None
    created_at: datetime


class ChatConversationListItem(BaseModel):
    id: int
    hiring_project_id: int | None
    title: str
    created_at: datetime
    updated_at: datetime


class ChatConversationRead(ChatConversationListItem):
    messages: list[ChatMessageRead]
