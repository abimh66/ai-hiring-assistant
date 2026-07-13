from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.deps import get_current_user
from app.db.session import get_session
from app.modules.auth.models import User
from app.modules.hiring_projects.schemas import (
    HiringProjectCreate,
    HiringProjectRead,
    HiringProjectUpdate,
)
from app.modules.hiring_projects.service import (
    create_hiring_project,
    delete_hiring_project,
    get_hiring_project_or_404,
    list_hiring_projects,
    update_hiring_project,
)

router = APIRouter(
    prefix="/hiring-projects",
    tags=["hiring-projects"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=list[HiringProjectRead])
def list_projects(session: Session = Depends(get_session)):
    return list_hiring_projects(session)


@router.post("", response_model=HiringProjectRead, status_code=201)
def create_project(
    payload: HiringProjectCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return create_hiring_project(session, payload, created_by=current_user.id)


@router.get("/{hiring_project_id}", response_model=HiringProjectRead)
def get_project(hiring_project_id: int, session: Session = Depends(get_session)):
    return get_hiring_project_or_404(session, hiring_project_id)


@router.patch("/{hiring_project_id}", response_model=HiringProjectRead)
def patch_project(
    hiring_project_id: int,
    payload: HiringProjectUpdate,
    session: Session = Depends(get_session),
):
    project = get_hiring_project_or_404(session, hiring_project_id)
    return update_hiring_project(session, project, payload)


@router.delete("/{hiring_project_id}", status_code=204)
def remove_project(hiring_project_id: int, session: Session = Depends(get_session)):
    project = get_hiring_project_or_404(session, hiring_project_id)
    delete_hiring_project(session, project)
