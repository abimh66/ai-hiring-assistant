from fastapi import APIRouter
from pydantic import BaseModel

from app.agents.shortlisting import ShortlistResult, shortlist_agent

router = APIRouter(tags=["shortlisting"])


class CandidateMatchSummary(BaseModel):
    application_id: int
    match_score: int
    strengths: list[str] = []
    weaknesses: list[str] = []
    missing_skills: list[str] = []


class ShortlistRequest(BaseModel):
    job_description: str
    candidates: list[CandidateMatchSummary]


@router.post("/shortlist")
def generate_shortlist(payload: ShortlistRequest) -> ShortlistResult:
    prompt = (
        f"Job description:\n{payload.job_description}\n\n"
        f"Candidates:\n{[c.model_dump() for c in payload.candidates]}"
    )
    run_output = shortlist_agent.run(prompt)
    return ShortlistResult.model_validate(run_output.content)
