from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.modules.applications.models import Application
from app.modules.candidate_matching.models import CandidateMatch
from app.modules.candidates.models import Candidate
from app.modules.chat_context.schemas import CandidateContext, MatchContext, ShortlistContext
from app.modules.hiring_projects.models import HiringProject
from app.modules.resume_analysis.models import ResumeAnalysis
from app.modules.shortlisting.models import ShortlistRecommendation


def owned_project_ids(session: Session, user_id: int) -> list[int]:
    rows = session.exec(
        select(HiringProject.id).where(HiringProject.created_by == user_id)
    ).all()
    return [int(r) for r in rows]


def _require_owned_project(session: Session, user_id: int, hiring_project_id: int) -> HiringProject:
    project = session.get(HiringProject, hiring_project_id)
    if project is None or project.created_by != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hiring project not found")
    return project


def _to_candidate_context(
    application: Application,
    project: HiringProject,
    candidate: Candidate | None,
    analysis: ResumeAnalysis | None,
    match: CandidateMatch | None,
) -> CandidateContext:
    return CandidateContext(
        application_id=int(application.id),
        candidate_id=candidate.id if candidate else None,
        candidate_name=candidate.full_name if candidate else "(unknown)",
        candidate_email=candidate.email if candidate else "(unknown)",
        hiring_project_id=int(project.id),
        project_title=project.title,
        application_status=application.status.value,
        summary=analysis.summary if analysis else None,
        skills=(analysis.skills or []) if analysis else [],
        experience=(analysis.experience or []) if analysis else [],
        education=(analysis.education or []) if analysis else [],
        strengths=(analysis.strengths or []) if analysis else [],
        concerns=(analysis.concerns or []) if analysis else [],
        match_score=match.match_score if match else None,
        match_status=match.status.value if match else None,
    )


def list_candidate_contexts(
    session: Session, user_id: int, hiring_project_id: int | None
) -> list[CandidateContext]:
    if hiring_project_id is not None:
        _require_owned_project(session, user_id, hiring_project_id)
        project_ids = [hiring_project_id]
    else:
        project_ids = owned_project_ids(session, user_id)
    if not project_ids:
        return []

    applications = session.exec(
        select(Application).where(Application.hiring_project_id.in_(project_ids))
    ).all()

    contexts: list[CandidateContext] = []
    for application in applications:
        project = session.get(HiringProject, application.hiring_project_id)
        candidate = (
            session.get(Candidate, application.candidate_id)
            if application.candidate_id is not None
            else None
        )
        analysis = session.exec(
            select(ResumeAnalysis).where(ResumeAnalysis.application_id == application.id)
        ).first()
        match = session.exec(
            select(CandidateMatch).where(CandidateMatch.application_id == application.id)
        ).first()
        contexts.append(_to_candidate_context(application, project, candidate, analysis, match))
    return contexts


def get_candidate_context(session: Session, user_id: int, application_id: int) -> CandidateContext:
    application = session.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    project = _require_owned_project(session, user_id, application.hiring_project_id)
    candidate = (
        session.get(Candidate, application.candidate_id)
        if application.candidate_id is not None
        else None
    )
    analysis = session.exec(
        select(ResumeAnalysis).where(ResumeAnalysis.application_id == application_id)
    ).first()
    match = session.exec(
        select(CandidateMatch).where(CandidateMatch.application_id == application_id)
    ).first()
    return _to_candidate_context(application, project, candidate, analysis, match)


def get_match_context(session: Session, user_id: int, application_id: int) -> MatchContext:
    application = session.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    _require_owned_project(session, user_id, application.hiring_project_id)
    match = session.exec(
        select(CandidateMatch).where(CandidateMatch.application_id == application_id)
    ).first()
    if match is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    return MatchContext(
        application_id=application_id,
        status=match.status.value,
        match_score=match.match_score,
        strengths=match.strengths or [],
        weaknesses=match.weaknesses or [],
        missing_skills=match.missing_skills or [],
        reasoning=match.reasoning,
    )


def get_shortlist_context(session: Session, user_id: int, hiring_project_id: int) -> ShortlistContext:
    _require_owned_project(session, user_id, hiring_project_id)
    shortlist = session.exec(
        select(ShortlistRecommendation).where(
            ShortlistRecommendation.hiring_project_id == hiring_project_id
        )
    ).first()
    if shortlist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shortlist not found")
    return ShortlistContext(
        hiring_project_id=hiring_project_id,
        status=shortlist.status.value,
        recommendations=shortlist.recommendations,
        overall_summary=shortlist.overall_summary,
    )
