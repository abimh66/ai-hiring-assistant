from agno.agent import Agent
from agno.models.openrouter import OpenRouter

from app.core.config import get_settings
from app.tools.chat_context import build_context_tools

settings = get_settings()


def _model() -> OpenRouter:
    return OpenRouter(
        id=settings.openrouter_model_id,
        api_key=settings.openrouter_api_key,
        max_tokens=8192,
    )


def _scope_note(hiring_project_id: int | None) -> str:
    if hiring_project_id is not None:
        return (
            f"You are scoped to hiring project {hiring_project_id}. "
            "When calling tools, restrict to this project."
        )
    return (
        "You are in global scope across all of the recruiter's hiring projects. "
        "Candidates may belong to different roles — always state which project a candidate is in."
    )


def _history_preamble(history: list[dict]) -> str:
    if not history:
        return ""
    lines = [f"{m['role'].upper()}: {m['content']}" for m in history]
    return "Conversation so far:\n" + "\n".join(lines) + "\n\n"


def build_chat_orchestrator(
    jwt: str,
    hiring_project_id: int | None,
    allowed_project_ids: list[int],
    history: list[dict],
) -> Agent:
    context_tools = build_context_tools(jwt, hiring_project_id, allowed_project_ids)
    spawn_state = {"count": 0}

    def make_specialist(topic: str, task: str) -> str:
        """Delegate a focused subtask to a specialist sub-agent.

        Use this for deep, self-contained work such as comparing candidates in detail. The
        specialist can retrieve data with the same tools you have. It cannot delegate further.

        Args:
            topic: The specialist's area of focus, e.g. "candidate comparison".
            task: A complete, self-contained instruction describing exactly what to produce.
        Returns:
            str: The specialist's finished answer, or a notice if the spawn limit was reached.
        """
        if spawn_state["count"] >= settings.max_specialist_spawns:
            return (
                "Specialist limit reached for this turn; answer directly with the data you have."
            )
        spawn_state["count"] += 1
        specialist = Agent(
            id="chat-specialist-agent",
            name=f"Specialist: {topic}",
            model=_model(),
            tools=build_context_tools(jwt, hiring_project_id, allowed_project_ids),
            markdown=True,
            instructions=[
                f"You are a specialist in {topic}.",
                "Complete the assigned task precisely and concisely.",
                "Ground every statement in data you retrieve with your tools — never invent "
                "candidates, scores, or skills.",
                "Return only the finished result; no preamble.",
            ],
        )
        result = specialist.run(task)
        return result.content if result and result.content else "(specialist produced no output)"

    instructions: list[str] = []
    preamble = _history_preamble(history).strip()
    if preamble:
        instructions.append(preamble)
    instructions.extend(
        [
            "You are an HR hiring copilot helping a recruiter reason about candidates.",
            "Always ground factual claims in data retrieved via your tools — never invent "
            "candidates, scores, skills, or reasoning.",
            "Prefer structured tools (list_candidates, get_candidate, get_match, get_shortlist) "
            "for precise questions; use search_resumes for free-text questions about resume content.",
            "When asked to compare candidates or perform a deep self-contained analysis, delegate "
            "to make_specialist with a clear topic and a complete task.",
            "Explain your reasoning and cite which candidate/field each statement comes from.",
            "If the data needed is missing or empty, say so honestly rather than guessing.",
            _scope_note(hiring_project_id),
        ]
    )

    orchestrator = Agent(
        id="chat-orchestrator-agent",
        name="Hiring Chat Orchestrator",
        model=_model(),
        tools=[*context_tools, make_specialist],
        markdown=True,
        instructions=instructions,
    )
    return orchestrator
