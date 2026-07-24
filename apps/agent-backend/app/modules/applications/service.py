import base64

from fastapi import HTTPException, UploadFile, status
from sqlmodel import Session, select

from app.modules.applications.models import Application
from app.modules.applications.schemas import ApplicationRead, ApplicationUpdate, ApplicationUploadResult
from app.modules.storage.client import make_key, upload_file
from app.worker.tasks import analyze_resume


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


MAX_BULK_UPLOAD_FILES = 20


async def create_applications_with_resumes(
    session: Session,
    hiring_project_id: int,
    resumes: list[UploadFile],
) -> list[ApplicationUploadResult]:
    if len(resumes) > MAX_BULK_UPLOAD_FILES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot upload more than {MAX_BULK_UPLOAD_FILES} resumes at once",
        )

    results: list[ApplicationUploadResult] = []
    for resume in resumes:
        filename = resume.filename or "resume"
        try:
            resume_bytes = await resume.read()
            # Reserve the object key synchronously (no network) and hand the
            # actual store write + analysis to the worker, so this request
            # returns immediately regardless of batch size.
            resume_key = make_key(filename)

            application = Application(
                candidate_id=None,
                hiring_project_id=hiring_project_id,
                resume_file_key=resume_key,
                resume_original_filename=filename,
            )
            session.add(application)
            session.commit()
            session.refresh(application)

            analyze_resume.delay(
                application.id,
                base64.b64encode(resume_bytes).decode("ascii"),
                resume.content_type,
            )

            results.append(
                ApplicationUploadResult(
                    filename=filename, application=ApplicationRead.model_validate(application)
                )
            )
        except Exception as exc:
            session.rollback()
            results.append(ApplicationUploadResult(filename=filename, error=str(exc)))

    return results


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

    from app.worker.tasks import extract_interview_notes

    extract_interview_notes.delay(application.id)
    return application


def set_interview_notes_text(
    session: Session, application: Application, text: str
) -> Application:
    application.interview_notes_text = text
    session.add(application)
    session.commit()
    session.refresh(application)
    return application
