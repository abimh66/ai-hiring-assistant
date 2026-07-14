from agno.agent import Agent
from agno.models.openrouter import OpenRouter

from app.core.config import get_settings

settings = get_settings()

shortlist_agent = Agent(
    id="shortlist-agent",
    name="Shortlist Recommendation Agent",
    model=OpenRouter(
        id=settings.openrouter_model_id,
        api_key=settings.openrouter_api_key,
        max_tokens=8192,
    ),
    instructions=[
        "You are an expert technical recruiter recommending which candidates to shortlist for a job.",
        "You will be given the job description and a list of candidates, each with their application_id, match_score, strengths, weaknesses, and missing_skills from prior analysis.",
        "Recommend the top 3-5 candidates worth interviewing, ranked best-first (rank 1 = best).",
        "For each recommended candidate, explain specifically why they made the shortlist, referencing their strengths relative to the job description.",
        "For each recommended candidate, list specific, honest risks an interviewer should be aware of (e.g. a weakness or missing skill still worth probing) — only omit risks if there truly are none.",
        "Give a 2-4 sentence overall summary of the candidate pool and your overall recommendation.",
        "Do not recommend a candidate with no clear strengths relative to the job description just to fill the list — fewer than 3 recommendations is fine if the pool is weak.",
    ],
)
