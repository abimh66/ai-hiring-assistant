from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.modules.candidate_matching.models import CandidateMatchStatus
from app.modules.hiring_projects.models import HiringProject
from app.modules.reports.models import HiringReport, ReportVersion, ReportVersionSource


def _require_owned_project(session: Session, user_id: int, hiring_project_id: int) -> HiringProject:
    project = session.get(HiringProject, hiring_project_id)
    if project is None or project.created_by != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hiring project not found")
    return project


def get_report_by_project_id(session: Session, hiring_project_id: int) -> HiringReport | None:
    return session.exec(
        select(HiringReport).where(HiringReport.hiring_project_id == hiring_project_id)
    ).first()


def get_current_version(session: Session, report: HiringReport) -> ReportVersion | None:
    if report.current_version_id is None:
        return None
    return session.get(ReportVersion, report.current_version_id)


def get_report_for_project(session: Session, user_id: int, hiring_project_id: int) -> HiringReport:
    _require_owned_project(session, user_id, hiring_project_id)
    report = get_report_by_project_id(session, hiring_project_id)
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return report


def get_report_or_404(session: Session, user_id: int, report_id: int) -> HiringReport:
    report = session.get(HiringReport, report_id)
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    _require_owned_project(session, user_id, report.hiring_project_id)
    return report


def _next_version_number(session: Session, report_id: int) -> int:
    versions = session.exec(
        select(ReportVersion).where(ReportVersion.report_id == report_id)
    ).all()
    return max((v.version_number for v in versions), default=0) + 1


def add_version(
    session: Session,
    report: HiringReport,
    content: str,
    source: ReportVersionSource,
    created_by: int,
) -> ReportVersion:
    version = ReportVersion(
        report_id=report.id,
        version_number=_next_version_number(session, report.id),
        content=content,
        source=source,
        created_by=created_by,
    )
    session.add(version)
    session.commit()
    session.refresh(version)

    report.current_version_id = version.id
    report.updated_at = datetime.now(timezone.utc)
    session.add(report)
    session.commit()
    session.refresh(report)
    return version


def get_or_create_pending_report(session: Session, hiring_project_id: int) -> HiringReport:
    report = get_report_by_project_id(session, hiring_project_id)
    if report is None:
        report = HiringReport(hiring_project_id=hiring_project_id)
    report.status = CandidateMatchStatus.pending
    report.error_message = None
    report.updated_at = datetime.now(timezone.utc)
    session.add(report)
    session.commit()
    session.refresh(report)
    return report


def mark_report_completed(
    session: Session, report: HiringReport, content: str, created_by: int
) -> HiringReport:
    add_version(session, report, content, ReportVersionSource.ai_generated, created_by)
    report.status = CandidateMatchStatus.completed
    report.error_message = None
    report.updated_at = datetime.now(timezone.utc)
    session.add(report)
    session.commit()
    session.refresh(report)
    return report


def mark_report_failed(
    session: Session, report: HiringReport, error_message: str
) -> HiringReport:
    report.status = CandidateMatchStatus.failed
    report.error_message = error_message
    report.updated_at = datetime.now(timezone.utc)
    session.add(report)
    session.commit()
    session.refresh(report)
    return report


def save_edited_version(
    session: Session, user_id: int, report_id: int, content: str, created_by: int
) -> ReportVersion:
    report = get_report_or_404(session, user_id, report_id)
    return add_version(session, report, content, ReportVersionSource.edited, created_by)


def restore_version(
    session: Session, user_id: int, report_id: int, version_id: int, created_by: int
) -> ReportVersion:
    report = get_report_or_404(session, user_id, report_id)
    source = session.get(ReportVersion, version_id)
    if source is None or source.report_id != report.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found")
    return add_version(session, report, source.content, ReportVersionSource.restored, created_by)


def list_versions(session: Session, user_id: int, report_id: int) -> list[ReportVersion]:
    get_report_or_404(session, user_id, report_id)
    return session.exec(
        select(ReportVersion)
        .where(ReportVersion.report_id == report_id)
        .order_by(ReportVersion.version_number.desc())
    ).all()
