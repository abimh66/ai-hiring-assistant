from fastapi import APIRouter
from pydantic import BaseModel

from app.agents.report import report_agent

router = APIRouter(tags=["report"])


class ReportCandidate(BaseModel):
    name: str
    match_score: int | None = None
    match_strengths: list[str] = []
    match_weaknesses: list[str] = []
    missing_skills: list[str] = []
    shortlist_rank: int | None = None
    shortlist_reasoning: str | None = None
    shortlist_risks: list[str] = []
    resume_summary: str | None = None
    skills: list[str] = []
    experience: list[dict] = []
    interview_notes_text: str | None = None


class ReportRequest(BaseModel):
    project_title: str
    job_description: str
    candidates: list[ReportCandidate]


@router.post("/report")
def generate_report(payload: ReportRequest) -> dict:
    prompt = (
        f"Project title: {payload.project_title}\n\n"
        f"Job description:\n{payload.job_description}\n\n"
        f"Shortlisted candidates:\n{[c.model_dump() for c in payload.candidates]}"
    )
    run_output = report_agent.run(prompt)
    return {"content": run_output.content}
