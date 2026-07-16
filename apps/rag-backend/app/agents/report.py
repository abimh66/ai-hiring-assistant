from agno.agent import Agent
from agno.models.openrouter import OpenRouter

from app.core.config import get_settings

settings = get_settings()

report_agent = Agent(
    id="report-agent",
    name="Hiring Report Agent",
    model=OpenRouter(
        id=settings.openrouter_model_id,
        api_key=settings.openrouter_api_key,
        max_tokens=8192,
    ),
    markdown=True,
    instructions=[
        "You are an expert technical recruiter writing a hiring report for a hiring manager.",
        "You will be given the job description, the project title, and a list of SHORTLISTED candidates.",
        "Each candidate includes: match_score, match strengths/weaknesses, missing skills, their shortlist rank and reasoning and risks, a resume summary with skills and experience, and (optionally) interview notes text.",
        "Write a single, well-structured Markdown document. Use this structure:",
        "1. An H1 title with the project/role title.",
        "2. A short 'Overview' paragraph summarizing the pool and your top-line recommendation.",
        "3. A 'Candidate Ranking' section: candidates in shortlist rank order, each as an H2 with the candidate name, followed by concise bullet lists for Strengths, Weaknesses / Risks, Missing skills, and a short 'Interview summary' paragraph derived from the interview notes (write 'No interview notes on file.' if none).",
        "4. A closing 'Recommendation' section naming who to advance and any decision risks.",
        "Ground every statement in the provided data. Do not invent facts, scores, or experience not present in the input.",
        "Return ONLY the Markdown document — no preamble, no code fences around the whole thing.",
    ],
)
