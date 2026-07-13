from fastapi import HTTPException, UploadFile, status
from sqlmodel import Session, select

from app.modules.applications.models import Application
from app.modules.applications.schemas import ApplicationCreate, ApplicationUpdate
from app.modules.candidates.service import get_or_create_candidate
from app.modules.storage.client import upload_file


def list_applications_for_project(session: Session, hiring_project_id: int) -> list[Application]:
    return list(
        session.exec(
            select(Application).where(Application.hiring_project_id == hiring_project_id)
        ).all()
    )


def list_applications_for_candidate(session: Session, candidate_id: int) -> list[Application]:
    return list(
        session.exec(select(Application).where(Application.candidate_id == candidate_id)).all()
    )


def get_application_or_404(session: Session, application_id: int) -> Application:
    application = session.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    return application


async def create_application_with_resume(
    session: Session,
    hiring_project_id: int,
    payload: ApplicationCreate,
    resume: UploadFile,
) -> Application:
    candidate = get_or_create_candidate(
        session, payload.candidate_email, payload.candidate_full_name, payload.candidate_phone
    )

    resume_bytes = await resume.read()
    resume_key = upload_file(resume_bytes, resume.filename or "resume", resume.content_type)

    application = Application(
        candidate_id=candidate.id,
        hiring_project_id=hiring_project_id,
        resume_file_key=resume_key,
    )
    session.add(application)
    session.commit()
    session.refresh(application)
    return application


def update_application_status(
    session: Session, application: Application, payload: ApplicationUpdate
) -> Application:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(application, field, value)
    session.add(application)
    session.commit()
    session.refresh(application)
    return application


async def upload_interview_notes(
    session: Session, application: Application, notes_file: UploadFile
) -> Application:
    notes_bytes = await notes_file.read()
    notes_key = upload_file(notes_bytes, notes_file.filename or "notes", notes_file.content_type)
    application.interview_notes_file_key = notes_key
    session.add(application)
    session.commit()
    session.refresh(application)
    return application
