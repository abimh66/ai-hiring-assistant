from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.modules.applications.models import Application
from app.modules.candidate_matching.service import get_or_create_pending_match
from app.modules.hiring_projects.models import HiringProject
from app.modules.hiring_projects.schemas import HiringProjectCreate, HiringProjectUpdate
from app.modules.resume_analysis.models import ResumeAnalysisStatus
from app.modules.resume_analysis.service import get_analysis_by_application_id
from app.worker.tasks import match_candidate


def list_hiring_projects(session: Session) -> list[HiringProject]:
    return list(session.exec(select(HiringProject)).all())


def get_hiring_project_or_404(session: Session, hiring_project_id: int) -> HiringProject:
    project = session.get(HiringProject, hiring_project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hiring project not found")
    return project


def create_hiring_project(session: Session, payload: HiringProjectCreate, created_by: int) -> HiringProject:
    project = HiringProject(**payload.model_dump(), created_by=created_by)
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


def update_hiring_project(
    session: Session, project: HiringProject, payload: HiringProjectUpdate
) -> HiringProject:
    update_data = payload.model_dump(exclude_unset=True)
    job_description_changed = (
        "job_description" in update_data
        and update_data["job_description"] != project.job_description
    )

    for field, value in update_data.items():
        setattr(project, field, value)
    session.add(project)
    session.commit()
    session.refresh(project)

    if job_description_changed:
        _rematch_project_applications(session, project.id)

    return project


def _rematch_project_applications(session: Session, hiring_project_id: int) -> None:
    applications = session.exec(
        select(Application).where(Application.hiring_project_id == hiring_project_id)
    ).all()
    for application in applications:
        analysis = get_analysis_by_application_id(session, application.id)
        if analysis is not None and analysis.status == ResumeAnalysisStatus.completed:
            get_or_create_pending_match(session, application.id)
            match_candidate.delay(application.id)


def delete_hiring_project(session: Session, project: HiringProject) -> None:
    session.delete(project)
    session.commit()
