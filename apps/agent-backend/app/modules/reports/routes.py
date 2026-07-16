from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.deps import get_current_user
from app.db.session import get_session
from app.modules.auth.models import User
from app.modules.reports.schemas import (
    ReportRead,
    ReportVersionRead,
    ReportVersionSummary,
    SaveVersionRequest,
)
from app.modules.reports.service import (
    get_current_version,
    get_or_create_pending_report,
    get_report_for_project,
    get_report_or_404,
    list_versions,
    restore_version,
    save_edited_version,
)
from app.worker.tasks import generate_report

router = APIRouter(
    prefix="/hiring-projects/{hiring_project_id}/report",
    tags=["reports"],
)


def _to_report_read(session: Session, report) -> ReportRead:
    current = get_current_version(session, report)
    return ReportRead(
        id=report.id,
        hiring_project_id=report.hiring_project_id,
        status=report.status,
        error_message=report.error_message,
        current_version_id=report.current_version_id,
        content=current.content if current else None,
        created_at=report.created_at,
        updated_at=report.updated_at,
    )


@router.post("", response_model=ReportRead)
def trigger_report(
    hiring_project_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    from app.modules.reports.service import _require_owned_project

    _require_owned_project(session, user.id, hiring_project_id)
    report = get_or_create_pending_report(session, hiring_project_id)
    generate_report.delay(hiring_project_id, user.id)
    return _to_report_read(session, report)


@router.get("", response_model=ReportRead)
def read_report(
    hiring_project_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    report = get_report_for_project(session, user.id, hiring_project_id)
    return _to_report_read(session, report)


@router.post("/versions", response_model=ReportRead)
def save_version(
    hiring_project_id: int,
    payload: SaveVersionRequest,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    report = get_report_for_project(session, user.id, hiring_project_id)
    save_edited_version(session, user.id, report.id, payload.content, user.id)
    session.refresh(report)
    return _to_report_read(session, report)


@router.post("/versions/{version_id}/restore", response_model=ReportRead)
def restore(
    hiring_project_id: int,
    version_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    report = get_report_for_project(session, user.id, hiring_project_id)
    restore_version(session, user.id, report.id, version_id, user.id)
    session.refresh(report)
    return _to_report_read(session, report)


@router.get("/versions", response_model=list[ReportVersionSummary])
def read_versions(
    hiring_project_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    report = get_report_for_project(session, user.id, hiring_project_id)
    return list_versions(session, user.id, report.id)


@router.get("/versions/{version_id}", response_model=ReportVersionRead)
def read_version(
    hiring_project_id: int,
    version_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    from fastapi import HTTPException, status

    from app.modules.reports.models import ReportVersion

    report = get_report_for_project(session, user.id, hiring_project_id)
    version = session.get(ReportVersion, version_id)
    if version is None or version.report_id != report.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found")
    return version
