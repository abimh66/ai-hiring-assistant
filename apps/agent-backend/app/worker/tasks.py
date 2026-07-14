import httpx
from sqlmodel import Session

from app.core.config import get_settings
from app.db.session import engine
from app.modules.applications.models import Application
from app.modules.candidates.models import Candidate
from app.modules.candidates.service import get_or_create_candidate
from app.modules.hiring_projects.models import HiringProject  # noqa: F401
from app.modules.resume_analysis.service import (
    get_analysis_by_application_id,
    get_or_create_pending_analysis,
    mark_analysis_completed,
    mark_analysis_failed,
    mark_embedding_completed,
    mark_embedding_failed,
)
from app.modules.storage.client import download_file
from app.worker.celery_app import celery_app

settings = get_settings()


@celery_app.task(name="ping")
def ping() -> str:
    return "pong"


@celery_app.task(name="analyze_resume")
def analyze_resume(application_id: int) -> None:
    with Session(engine) as session:
        analysis = get_or_create_pending_analysis(session, application_id)

        application = session.get(Application, application_id)
        if application is None:
            mark_analysis_failed(session, analysis, "Application not found")
            return

        try:
            resume_bytes = download_file(application.resume_file_key)
            response = httpx.post(
                f"{settings.rag_backend_url}/resume-analysis",
                files={"resume": (application.resume_original_filename, resume_bytes)},
                timeout=120,
            )
            response.raise_for_status()
            result = response.json()
        except Exception as exc:
            mark_analysis_failed(session, analysis, str(exc))
            return

        candidate_email = result.get("candidate_email")
        if not candidate_email:
            mark_analysis_failed(
                session, analysis, "Could not extract a candidate email from the resume"
            )
            return

        candidate = get_or_create_candidate(
            session,
            candidate_email,
            result.get("candidate_full_name") or "Unknown",
            result.get("candidate_phone"),
        )
        application.candidate_id = candidate.id
        session.add(application)
        session.commit()

        analysis = mark_analysis_completed(
            session, analysis, result, result["extraction_method"], result["extracted_text"]
        )

        _embed(session, application, candidate, analysis)


@celery_app.task(name="embed_resume")
def embed_resume(application_id: int) -> None:
    with Session(engine) as session:
        application = session.get(Application, application_id)
        if application is None or application.candidate_id is None:
            return

        candidate = session.get(Candidate, application.candidate_id)
        analysis = get_analysis_by_application_id(session, application_id)
        if candidate is None or analysis is None or analysis.extracted_text is None:
            return

        _embed(session, application, candidate, analysis)


def _embed(session: Session, application: Application, candidate: Candidate, analysis) -> None:
    try:
        response = httpx.post(
            f"{settings.rag_backend_url}/resume-embed",
            json={
                "application_id": application.id,
                "candidate_id": candidate.id,
                "hiring_project_id": application.hiring_project_id,
                "resume_analysis_id": analysis.id,
                "candidate_name": candidate.full_name,
                "candidate_email": candidate.email,
                "skills": analysis.skills or [],
                "extraction_method": analysis.extraction_method or "unknown",
                "text_content": analysis.extracted_text,
            },
            timeout=120,
        )
        response.raise_for_status()
    except Exception as exc:
        mark_embedding_failed(session, analysis, str(exc))
        return

    mark_embedding_completed(session, analysis)
