FROM python:3.12-slim

RUN pip install --no-cache-dir uv

WORKDIR /workspace

COPY pyproject.toml uv.lock ./
COPY apps/rag-backend apps/rag-backend
RUN uv sync --package rag-backend

WORKDIR /workspace/apps/rag-backend
ENV PATH="/workspace/.venv/bin:$PATH"

EXPOSE 7777

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7777"]
