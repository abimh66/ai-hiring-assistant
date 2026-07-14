from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from pydantic import BaseModel

from app.core.config import get_settings

settings = get_settings()


class ExperienceEntry(BaseModel):
    company: str
    title: str
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None


class EducationEntry(BaseModel):
    institution: str
    degree: str | None = None
    field: str | None = None
    start_date: str | None = None
    end_date: str | None = None


class ResumeProfile(BaseModel):
    candidate_full_name: str | None = None
    candidate_email: str | None = None
    candidate_phone: str | None = None
    summary: str
    skills: list[str]
    experience: list[ExperienceEntry]
    education: list[EducationEntry]
    strengths: list[str]
    concerns: list[str]
    suggested_interview_topics: list[str]


resume_analysis_agent = Agent(
    id="resume-analysis-agent",
    name="Resume Analysis Agent",
    model=OpenRouter(
        id=settings.openrouter_model_id, api_key=settings.openrouter_api_key
    ),
    output_schema=ResumeProfile,
    markdown=True,
    instructions=[
        "You are an expert technical recruiter analyzing a candidate's resume.",
        "You will be given the plain-text contents of a resume. Extract a structured profile from it.",
        "`candidate_full_name` is the candidate's full name as it appears on the resume, or null if you cannot find one.",
        "`candidate_email` is the candidate's email address as it appears on the resume, or null if none is present. Do not invent one.",
        "`candidate_phone` is the candidate's phone number as it appears on the resume, or null if none is present.",
        "`summary` is a concise 2-4 sentence overview of the candidate's background and seniority.",
        "`skills` is a flat list of concrete skills (technologies, tools, languages, methodologies) mentioned in the resume.",
        "`experience` and `education` should preserve the resume's own entries — do not invent employers, titles, or schools.",
        "Dates should stay in whatever format the resume uses (e.g. 'Jan 2021'); use null when a date is missing or the role is current.",
        "`strengths` are notable positives for a hiring manager (e.g. depth in a relevant stack, career progression, leadership).",
        "`concerns` are honest, specific potential red flags (e.g. employment gaps, frequent job-hopping, unclear scope of past roles) — return an empty list if there are none.",
        "`suggested_interview_topics` are specific questions or areas an interviewer should probe based on this particular resume.",
    ],
)
