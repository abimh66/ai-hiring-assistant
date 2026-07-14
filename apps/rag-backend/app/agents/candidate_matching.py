from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from pydantic import BaseModel

from app.core.config import get_settings

settings = get_settings()


class CandidateMatchResult(BaseModel):
    match_score: int  # 0-100
    strengths: list[str]
    weaknesses: list[str]
    missing_skills: list[str]
    reasoning: str


candidate_matching_agent = Agent(
    id="candidate-matching-agent",
    name="Candidate Matching Agent",
    model=OpenRouter(
        id=settings.openrouter_model_id,
        api_key=settings.openrouter_api_key,
        max_tokens=8192,
    ),
    output_schema=CandidateMatchResult,
    markdown=True,
    instructions=[
        "You are an expert technical recruiter scoring how well a candidate fits a specific job description.",
        "You will be given the job description and the candidate's structured resume profile (summary, skills, experience, education, strengths, concerns).",
        "`match_score` is 0-100: how well this candidate's background fits THIS job description specifically, not a general quality score.",
        "`strengths` are specific ways this candidate's background matches the job description's requirements.",
        "`weaknesses` are specific gaps or mismatches relative to the job description — be honest and concrete.",
        "`missing_skills` are requirements or technologies explicitly or implicitly required by the job description that don't appear in the candidate's skills/experience.",
        "`reasoning` is a short paragraph explaining the score, referencing specific job description requirements and specific resume details.",
    ],
)
