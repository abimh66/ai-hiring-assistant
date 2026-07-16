from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from app.core.deps import get_current_user
from app.db.session import get_session
from app.modules.auth.models import User
from app.modules.chat.schemas import (
    ChatConversationListItem,
    ChatConversationRead,
    ChatMessageRead,
)
from app.modules.chat.service import (
    delete_conversation,
    get_conversation_or_404,
    list_conversations,
    list_messages,
)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/conversations", response_model=list[ChatConversationListItem])
def get_conversations(
    hiring_project_id: int | None = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return list_conversations(session, current_user.id, hiring_project_id)


@router.get("/conversations/{conversation_id}", response_model=ChatConversationRead)
def get_conversation(
    conversation_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    conversation = get_conversation_or_404(session, current_user.id, conversation_id)
    messages = [ChatMessageRead.model_validate(m, from_attributes=True) for m in
                list_messages(session, conversation_id)]
    return ChatConversationRead(
        id=conversation.id,
        hiring_project_id=conversation.hiring_project_id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=messages,
    )


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_conversation(
    conversation_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    conversation = get_conversation_or_404(session, current_user.id, conversation_id)
    delete_conversation(session, conversation)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
