import json
from collections.abc import Callable

import httpx

from app.core.config import get_settings
from app.knowledge import resumes_knowledge

settings = get_settings()


def build_context_tools(
    jwt: str,
    hiring_project_id: int | None,
    allowed_project_ids: list[int],
) -> list[Callable]:
    """Build data-access tools bound to one user's JWT and chat scope.

    All HTTP tools call agent-backend's owner-scoped /chat-context endpoints; ownership is
    therefore enforced server-side by the propagated JWT. `search_resumes` is filtered to
    `allowed_project_ids` so semantic search cannot leak other users' or other projects' data.
    """
    headers = {"Authorization": f"Bearer {jwt}"}
    base = settings.agent_backend_url.rstrip("/")

    def _get(path: str, params: dict | None = None) -> str:
        try:
            resp = httpx.get(f"{base}{path}", headers=headers, params=params, timeout=30.0)
        except httpx.HTTPError as exc:
            return json.dumps({"error": f"request failed: {exc}"})
        if resp.status_code == 404:
            return json.dumps({"error": "not found or not accessible"})
        if resp.status_code != 200:
            return json.dumps({"error": f"http {resp.status_code}"})
        return resp.text

    def list_candidates(hiring_project_id: int | None = None) -> str:
        """List candidates with their resume profile and match summary.

        Args:
            hiring_project_id: Restrict to one hiring project. Omit to include all projects
                in the current chat scope.
        Returns:
            str: JSON array of candidate context objects.
        """
        params = {}
        if hiring_project_id is not None:
            params["hiring_project_id"] = hiring_project_id
        return _get("/chat-context/candidates", params or None)

    def get_candidate(application_id: int) -> str:
        """Get one candidate's full profile (summary, skills, experience, education) plus match summary.

        Args:
            application_id: The application id identifying the candidate in a project.
        Returns:
            str: JSON candidate context object, or an error object.
        """
        return _get(f"/chat-context/candidates/{application_id}")

    def get_match(application_id: int) -> str:
        """Get the AI match result for a candidate: score, strengths, weaknesses, missing skills, and reasoning.

        Args:
            application_id: The application id.
        Returns:
            str: JSON match context object, or an error object.
        """
        return _get(f"/chat-context/matches/{application_id}")

    def get_shortlist(hiring_project_id: int) -> str:
        """Get the AI shortlist recommendation for a hiring project: ranked candidates, reasoning, risks.

        Args:
            hiring_project_id: The hiring project id.
        Returns:
            str: JSON shortlist context object, or an error object.
        """
        return _get(f"/chat-context/shortlist/{hiring_project_id}")

    def search_resumes(query: str) -> str:
        """Semantically search resume text across the candidates in scope.

        Use this for free-text questions about resume content that structured fields don't answer
        (e.g. "who mentioned leading a migration?").

        Args:
            query: A natural-language search query.
        Returns:
            str: JSON array of {candidate_name, application_id, hiring_project_id, excerpt}.
        """
        scope_ids = [hiring_project_id] if hiring_project_id is not None else allowed_project_ids
        if not scope_ids:
            return json.dumps([])
        try:
            docs = resumes_knowledge.search(
                query=query,
                max_results=5,
                filters={"hiring_project_id": {"$in": scope_ids}},
            )
        except Exception as exc:  # chroma/embedder errors must not crash the turn
            return json.dumps({"error": f"search failed: {type(exc).__name__}"})
        results = [
            {
                "candidate_name": d.meta_data.get("candidate_name"),
                "application_id": d.meta_data.get("application_id"),
                "hiring_project_id": d.meta_data.get("hiring_project_id"),
                "excerpt": (d.content or "")[:600],
            }
            for d in docs
        ]
        return json.dumps(results)

    return [list_candidates, get_candidate, get_match, get_shortlist, search_resumes]
