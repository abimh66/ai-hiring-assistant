import json
from collections.abc import AsyncIterator

from agno.run.agent import RunEvent
from fastapi import APIRouter, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.agents.chat_orchestrator import build_chat_orchestrator

router = APIRouter(tags=["chat"])


class ChatStreamRequest(BaseModel):
    message: str
    hiring_project_id: int | None = None
    allowed_project_ids: list[int] = []
    history: list[dict] = []


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def _extract_topic(tool) -> str:
    args = getattr(tool, "tool_args", None) or {}
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except json.JSONDecodeError:
            args = {}
    return args.get("topic", "specialist")


@router.post("/chat/stream")
async def chat_stream(payload: ChatStreamRequest, authorization: str = Header(...)):
    jwt = authorization.removeprefix("Bearer ").strip()

    async def event_source() -> AsyncIterator[str]:
        agent = build_chat_orchestrator(
            jwt=jwt,
            hiring_project_id=payload.hiring_project_id,
            allowed_project_ids=payload.allowed_project_ids,
            history=payload.history,
        )
        try:
            async for ev in agent.arun(payload.message, stream=True, stream_events=True):
                name = getattr(ev, "event", None)
                if name == RunEvent.run_content.value:
                    if ev.content:
                        yield _sse("text_delta", {"text": ev.content})
                elif name == RunEvent.tool_call_started.value:
                    tool_name = ev.tool.tool_name if ev.tool else "tool"
                    if tool_name == "make_specialist":
                        yield _sse("specialist_spawned", {"topic": _extract_topic(ev.tool)})
                    else:
                        yield _sse("tool_call", {"tool": tool_name})
                elif name == RunEvent.tool_call_completed.value:
                    tool_name = ev.tool.tool_name if ev.tool else "tool"
                    yield _sse("tool_result", {"tool": tool_name, "status": "ok"})
                elif name == RunEvent.run_error.value:
                    yield _sse("error", {"message": str(getattr(ev, "content", "run error"))})
                elif name == RunEvent.run_completed.value:
                    yield _sse("done", {"finish_reason": "stop"})
        except Exception as exc:  # never leak a raw 500 mid-stream
            yield _sse("error", {"message": f"{type(exc).__name__}: {exc}"})

    return StreamingResponse(event_source(), media_type="text/event-stream")
