from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.modules.hiring_projects.models import HiringProject
from app.modules.hiring_projects.schemas import HiringProjectCreate, HiringProjectUpdate


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
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


def delete_hiring_project(session: Session, project: HiringProject) -> None:
    session.delete(project)
    session.commit()
