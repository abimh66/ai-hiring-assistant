from fastapi import APIRouter
from pydantic import BaseModel

from app.agents.candidate_matching import CandidateMatchResult, candidate_matching_agent

router = APIRouter(tags=["candidate-matching"])


class ResumeProfileInput(BaseModel):
    summary: str | None = None
    skills: list[str] = []
    experience: list[dict] = []
    education: list[dict] = []
    strengths: list[str] = []
    concerns: list[str] = []


class CandidateMatchRequest(BaseModel):
    job_description: str
    resume_profile: ResumeProfileInput


@router.post("/candidate-match")
def match_candidate(payload: CandidateMatchRequest) -> CandidateMatchResult:
    prompt = (
        f"Job description:\n{payload.job_description}\n\n"
        f"Candidate profile:\n{payload.resume_profile.model_dump_json()}"
    )
    run_output = candidate_matching_agent.run(prompt)
    return CandidateMatchResult.model_validate(run_output.content)
