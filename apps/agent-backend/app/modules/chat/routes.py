from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials
from sqlmodel import Session

from app.core.deps import bearer_scheme, get_current_user
from app.db.session import get_session
from app.modules.auth.models import User
from app.modules.chat.models import ChatRole
from app.modules.chat.schemas import (
    ChatConversationListItem,
    ChatConversationRead,
    ChatMessageRead,
    ChatSendRequest,
)
from app.modules.chat.service import (
    append_message,
    create_conversation,
    delete_conversation,
    get_conversation_or_404,
    history_for_agent,
    list_conversations,
    list_messages,
    validate_project_scope,
)
from app.modules.chat.stream import proxy_chat_stream
from app.modules.chat_context.service import owned_project_ids

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("")
def send_chat_message(
    payload: ChatSendRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    validate_project_scope(session, current_user.id, payload.hiring_project_id)

    if payload.conversation_id is None:
        conversation = create_conversation(
            session, current_user.id, payload.hiring_project_id, payload.message
        )
    else:
        conversation = get_conversation_or_404(session, current_user.id, payload.conversation_id)

    history = history_for_agent(session, conversation.id)
    append_message(session, conversation.id, ChatRole.user, payload.message)

    if payload.hiring_project_id is not None:
        allowed_ids = [payload.hiring_project_id]
    else:
        allowed_ids = owned_project_ids(session, current_user.id)

    stream = proxy_chat_stream(
        session=session,
        conversation_id=conversation.id,
        jwt=credentials.credentials,
        message=payload.message,
        hiring_project_id=payload.hiring_project_id,
        allowed_project_ids=allowed_ids,
        history=history,
    )
    return StreamingResponse(stream, media_type="text/event-stream")


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
