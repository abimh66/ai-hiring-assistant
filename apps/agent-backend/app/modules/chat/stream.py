import json
from collections.abc import AsyncIterator

import httpx
from sqlmodel import Session

from app.core.config import get_settings
from app.modules.chat.models import ChatRole
from app.modules.chat.service import append_message

settings = get_settings()


def sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


async def proxy_chat_stream(
    session: Session,
    conversation_id: int,
    jwt: str,
    message: str,
    hiring_project_id: int | None,
    allowed_project_ids: list[int],
    history: list[dict],
) -> AsyncIterator[str]:
    """Stream from rag-backend, re-emit the SSE protocol, and persist the assistant turn.

    `history` must be the prior messages only (it must NOT include the new user message, which is
    passed separately as `message`).
    """
    yield sse("message_start", {"conversation_id": conversation_id})

    assistant_text: list[str] = []
    activity: list[dict] = []
    body = {
        "message": message,
        "hiring_project_id": hiring_project_id,
        "allowed_project_ids": allowed_project_ids,
        "history": history,
    }
    url = f"{settings.rag_backend_url.rstrip('/')}/chat/stream"
    headers = {"Authorization": f"Bearer {jwt}"}

    def persist(status_note: str | None) -> None:
        text = "".join(assistant_text)
        if status_note and not text:
            text = status_note
        append_message(
            session, conversation_id, ChatRole.assistant, text, activity=activity or None
        )

    try:
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("POST", url, json=body, headers=headers) as resp:
                if resp.status_code != 200:
                    await resp.aread()
                    yield sse("error", {"message": f"rag-backend http {resp.status_code}"})
                    persist("[assistant failed to respond]")
                    return
                event_name = None
                async for line in resp.aiter_lines():
                    if line.startswith("event:"):
                        event_name = line[len("event:"):].strip()
                    elif line.startswith("data:"):
                        data = json.loads(line[len("data:"):].strip())
                        if event_name == "text_delta":
                            assistant_text.append(data.get("text", ""))
                        elif event_name in ("tool_call", "specialist_spawned", "tool_result"):
                            activity.append({"type": event_name, **data})
                        # re-emit every event to the client verbatim
                        yield sse(event_name, data)
                        if event_name == "done":
                            persist(None)
                            return
                        if event_name == "error":
                            persist("[assistant failed to respond]")
                            return
        # stream ended without an explicit done/error
        persist(None)
        yield sse("done", {"finish_reason": "eos"})
    except httpx.HTTPError as exc:
        yield sse("error", {"message": f"stream failed: {exc}"})
        persist("[assistant failed to respond]")
