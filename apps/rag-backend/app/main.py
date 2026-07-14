from agno.models.base import Model
from typing import cast

from agno.db.postgres import PostgresDb
from agno.os import AgentOS
from agno.registry import Registry
from fastapi import FastAPI

from app.agents.candidate_matching import candidate_matching_agent
from app.agents.resume_analysis import resume_analysis_agent
from app.agents.shortlisting import shortlist_agent
from app.api.resume_analysis import router as resume_analysis_router
from app.api.resume_embed import router as resume_embed_router
from app.core.config import get_settings

settings = get_settings()

db = PostgresDb(db_url=settings.agno_database_url)

registry = Registry(
    name="rag-backend Registry",
    models=[
        cast(Model, resume_analysis_agent.model),
        cast(Model, candidate_matching_agent.model),
        cast(Model, shortlist_agent.model),
    ],
    dbs=[db],
)

base_app = FastAPI()
base_app.include_router(resume_analysis_router)
base_app.include_router(resume_embed_router)

agent_os = AgentOS(
    id="rag-backend",
    description="Resume intelligence agents for the AI Hiring Assistant",
    agents=[resume_analysis_agent, candidate_matching_agent, shortlist_agent],
    registry=registry,
    db=db,
    base_app=base_app,
)

app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(app="app.main:app", host="0.0.0.0", port=7777, reload=True)
