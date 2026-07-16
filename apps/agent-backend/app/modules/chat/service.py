from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.modules.chat.models import ChatConversation, ChatMessage, ChatRole
from app.modules.hiring_projects.models import HiringProject


def validate_project_scope(session: Session, user_id: int, hiring_project_id: int | None) -> None:
    if hiring_project_id is None:
        return
    project = session.get(HiringProject, hiring_project_id)
    if project is None or project.created_by != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hiring project not found")


def create_conversation(
    session: Session, user_id: int, hiring_project_id: int | None, first_message: str
) -> ChatConversation:
    title = first_message.strip()[:80] or "New conversation"
    conversation = ChatConversation(
        user_id=user_id, hiring_project_id=hiring_project_id, title=title
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


def get_conversation_or_404(
    session: Session, user_id: int, conversation_id: int
) -> ChatConversation:
    conversation = session.get(ChatConversation, conversation_id)
    if conversation is None or conversation.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return conversation


def list_conversations(
    session: Session, user_id: int, hiring_project_id: int | None
) -> list[ChatConversation]:
    statement = select(ChatConversation).where(ChatConversation.user_id == user_id)
    if hiring_project_id is not None:
        statement = statement.where(ChatConversation.hiring_project_id == hiring_project_id)
    statement = statement.order_by(ChatConversation.updated_at.desc())
    return list(session.exec(statement).all())


def list_messages(session: Session, conversation_id: int) -> list[ChatMessage]:
    return list(
        session.exec(
            select(ChatMessage)
            .where(ChatMessage.conversation_id == conversation_id)
            .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
        ).all()
    )


def history_for_agent(session: Session, conversation_id: int) -> list[dict]:
    return [
        {"role": m.role.value, "content": m.content}
        for m in list_messages(session, conversation_id)
    ]


def append_message(
    session: Session,
    conversation_id: int,
    role: ChatRole,
    content: str,
    activity: list[dict] | None = None,
) -> ChatMessage:
    message = ChatMessage(
        conversation_id=conversation_id, role=role, content=content, activity=activity
    )
    session.add(message)
    conversation = session.get(ChatConversation, conversation_id)
    if conversation is not None:
        conversation.updated_at = datetime.now(timezone.utc)
        session.add(conversation)
    session.commit()
    session.refresh(message)
    return message


def delete_conversation(session: Session, conversation: ChatConversation) -> None:
    for message in list_messages(session, conversation.id):
        session.delete(message)
    # Flush the child deletes before removing the parent: there is no ORM relationship
    # declaring the dependency, so without this the unit of work may emit the parent DELETE
    # first and violate the chat_messages FK.
    session.flush()
    session.delete(conversation)
    session.commit()
