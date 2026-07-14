from fastapi import APIRouter, File, UploadFile

from app.agents.resume_analysis import ResumeProfile, resume_analysis_agent
from app.parsing.extract_text import extract_text

router = APIRouter(tags=["resume-analysis"])


@router.post("/resume-analysis")
async def analyze_resume(resume: UploadFile = File(...)) -> dict:
    file_bytes = await resume.read()
    text, extraction_method = extract_text(file_bytes, resume.filename or "resume")

    run_output = resume_analysis_agent.run(text)
    profile: ResumeProfile = ResumeProfile.model_validate(run_output.content)

    return {
        **profile.model_dump(),
        "extraction_method": extraction_method,
        "extracted_text": text,
    }
