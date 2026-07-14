from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

from app.knowledge import resumes_knowledge

router = APIRouter(tags=["resume-analysis"])


class ResumeEmbedRequest(BaseModel):
    application_id: int
    candidate_id: int
    hiring_project_id: int
    resume_analysis_id: int
    candidate_name: str
    candidate_email: str
    skills: list[str]
    extraction_method: str
    text_content: str


@router.post("/resume-embed")
async def embed_resume(payload: ResumeEmbedRequest) -> dict:
    resumes_knowledge.insert(
        text_content=payload.text_content,
        metadata={
            "application_id": payload.application_id,
            "candidate_id": payload.candidate_id,
            "hiring_project_id": payload.hiring_project_id,
            "resume_analysis_id": payload.resume_analysis_id,
            "candidate_name": payload.candidate_name,
            "candidate_email": payload.candidate_email,
            "skills": payload.skills,
            "document_type": "resume",
            "extraction_method": payload.extraction_method,
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    return {"embedded": True}
