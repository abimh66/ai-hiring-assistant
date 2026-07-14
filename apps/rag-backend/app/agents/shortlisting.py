from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from pydantic import BaseModel

from app.core.config import get_settings

settings = get_settings()


class ShortlistEntry(BaseModel):
    application_id: int
    rank: int
    recommendation_reasoning: str
    risks: list[str]
    # No match_score here: the agent already received it as input (in `candidates`) and
    # doesn't need to authoritatively echo it back. The generate_shortlist Celery task
    # re-attaches the real match_score from Postgres before persisting.


class ShortlistResult(BaseModel):
    recommendations: list[ShortlistEntry]
    overall_summary: str


shortlist_agent = Agent(
    id="shortlist-agent",
    name="Shortlist Recommendation Agent",
    model=OpenRouter(
        id=settings.openrouter_model_id,
        api_key=settings.openrouter_api_key,
        max_tokens=8192,
    ),
    output_schema=ShortlistResult,
    markdown=True,
    instructions=[
        "You are an expert technical recruiter recommending which candidates to shortlist for a job.",
        "You will be given the job description and a list of candidates, each with their application_id, match_score, strengths, weaknesses, and missing_skills from prior analysis.",
        "Recommend the top 3-5 candidates worth interviewing, ranked best-first via `rank` (1 = best).",
        "`recommendation_reasoning` explains specifically why this candidate made the shortlist, referencing their strengths relative to the job description.",
        "`risks` are specific, honest concerns an interviewer should be aware of for this candidate (e.g. a weakness or missing skill that's still worth probing) — return an empty list only if there are truly none.",
        "`overall_summary` is a 2-4 sentence summary of the candidate pool and your overall recommendation.",
        "Do not recommend a candidate with no clear strengths relative to the job description just to fill the list — fewer than 3 recommendations is fine if the pool is weak.",
    ],
)
