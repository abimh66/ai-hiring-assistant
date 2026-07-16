from pydantic import BaseModel


class CandidateContext(BaseModel):
    application_id: int
    candidate_id: int | None
    candidate_name: str
    candidate_email: str
    hiring_project_id: int
    project_title: str
    application_status: str
    summary: str | None = None
    skills: list[str] = []
    experience: list[dict] = []
    education: list[dict] = []
    strengths: list[str] = []
    concerns: list[str] = []
    match_score: int | None = None
    match_status: str | None = None


class MatchContext(BaseModel):
    application_id: int
    status: str
    match_score: int | None = None
    strengths: list[str] = []
    weaknesses: list[str] = []
    missing_skills: list[str] = []
    reasoning: str | None = None


class ShortlistContext(BaseModel):
    hiring_project_id: int
    status: str
    recommendations: list[dict] | None = None
    overall_summary: str | None = None
