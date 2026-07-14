from agno.knowledge.embedder.fastembed import FastEmbedEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.chroma import ChromaDb

from app.core.config import get_settings

settings = get_settings()

resumes_knowledge = Knowledge(
    name="Resumes",
    vector_db=ChromaDb(
        collection=settings.chroma_collection,
        path=settings.chroma_path,
        persistent_client=True,
        embedder=FastEmbedEmbedder(id=settings.fastembed_model_id),
    ),
)
