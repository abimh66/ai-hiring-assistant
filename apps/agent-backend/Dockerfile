FROM python:3.12-slim

RUN pip install --no-cache-dir uv

WORKDIR /workspace

COPY pyproject.toml uv.lock ./
COPY apps/agent-backend apps/agent-backend
RUN uv sync --package agent-backend

WORKDIR /workspace/apps/agent-backend
ENV PATH="/workspace/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
