from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_ENV_FILE = Path(__file__).resolve().parents[4] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_ENV_FILE, extra="ignore")

    openrouter_api_key: str = ""
    openrouter_model_id: str = "openai/gpt-5-mini"

    mistral_api_key: str = ""
    mistral_ocr_model_id: str = "mistral-ocr-latest"

    agno_database_url: str = (
        "postgresql+psycopg://postgres:postgres@localhost:5432/agno"
    )

    chroma_path: str = "tmp/chroma"
    chroma_collection: str = "resumes"
    fastembed_model_id: str = "BAAI/bge-small-en-v1.5"

    ocr_min_chars_per_page: int = 100


@lru_cache
def get_settings() -> Settings:
    return Settings()
