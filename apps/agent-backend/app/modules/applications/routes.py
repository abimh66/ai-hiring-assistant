from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlmodel import Session

from app.core.deps import get_current_user
from app.db.session import get_session
from app.modules.applications.schemas import ApplicationRead, ApplicationUpdate, ApplicationUploadResult
from app.modules.applications.service import (
    create_applications_with_resumes,
    get_application_or_404,
    list_applications_for_project,
    update_application_status,
    upload_interview_notes,
)
from app.modules.hiring_projects.service import get_hiring_project_or_404
from app.modules.storage.client import get_file_url

project_applications_router = APIRouter(
    prefix="/hiring-projects/{hiring_project_id}/applications",
    tags=["applications"],
    dependencies=[Depends(get_current_user)],
)

applications_router = APIRouter(
    prefix="/applications",
    tags=["applications"],
    dependencies=[Depends(get_current_user)],
)


@project_applications_router.get("", response_model=list[ApplicationRead])
def list_project_applications(hiring_project_id: int, session: Session = Depends(get_session)):
    get_hiring_project_or_404(session, hiring_project_id)
    return list_applications_for_project(session, hiring_project_id)


@project_applications_router.post("", response_model=list[ApplicationUploadResult], status_code=201)
async def create_applications(
    hiring_project_id: int,
    resumes: list[UploadFile] = File(...),
    session: Session = Depends(get_session),
):
    get_hiring_project_or_404(session, hiring_project_id)
    return await create_applications_with_resumes(session, hiring_project_id, resumes)


@applications_router.get("/{application_id}", response_model=ApplicationRead)
def get_application(application_id: int, session: Session = Depends(get_session)):
    return get_application_or_404(session, application_id)


@applications_router.patch("/{application_id}", response_model=ApplicationRead)
def patch_application(
    application_id: int,
    payload: ApplicationUpdate,
    session: Session = Depends(get_session),
):
    application = get_application_or_404(session, application_id)
    return update_application_status(session, application, payload)


@applications_router.post("/{application_id}/interview-notes", response_model=ApplicationRead)
async def add_interview_notes(
    application_id: int,
    notes: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    application = get_application_or_404(session, application_id)
    return await upload_interview_notes(session, application, notes)


@applications_router.get("/{application_id}/resume-url")
def get_resume_url(application_id: int, session: Session = Depends(get_session)) -> dict[str, str]:
    application = get_application_or_404(session, application_id)
    return {"url": get_file_url(application.resume_file_key)}


@applications_router.get("/{application_id}/interview-notes-url")
def get_interview_notes_url(
    application_id: int, session: Session = Depends(get_session)
) -> dict[str, str]:
    application = get_application_or_404(session, application_id)
    if application.interview_notes_file_key is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No interview notes uploaded")
    return {"url": get_file_url(application.interview_notes_file_key)}
