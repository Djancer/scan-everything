from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    telegram_bot_token: str | None = None
    telegram_allowed_user_ids: str | None = None
    max_file_mb: int = Field(default=20, ge=1, le=200)
    llm_provider: Literal["openai", "mock", "local", "ollama"] = "local"
    ollama_base_url: str = 'http://127.0.0.1:11435'
    ollama_model: str = 'qwen3-vl:4b-instruct'
    ollama_timeout: int = 600
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str | None = None

    ocr_provider: Literal["tesseract", "disabled"] = "tesseract"
    tesseract_cmd: str | None = None
    tesseract_lang: str = "eng+deu"

    data_dir: Path = Path("data")
    database_path: Path = Path("data/documents.db")
    max_llm_chars: int = Field(default=50_000, ge=1_000, le=500_000)
    log_level: str = "INFO"

    @field_validator(
        "telegram_bot_token",
        "telegram_allowed_user_ids",
        "openai_api_key",
        "openai_base_url",
        "tesseract_cmd",
        mode="before",
    )
    @classmethod
    def empty_to_none(cls, value: object) -> object:
        return None if value == "" else value

    @field_validator("data_dir", "database_path", mode="after")
    @classmethod
    def absolute_path(cls, value: Path) -> Path:
        return value.expanduser().resolve()

    def validate_runtime(self) -> None:
        if not self.telegram_bot_token:
            raise ValueError(
                "TELEGRAM_BOT_TOKEN is missing. Copy .env.example to .env and add the token."
            )
        if self.llm_provider == "openai" and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai.")

    @property
    def allowed_user_ids(self) -> set[int]:
        if not self.telegram_allowed_user_ids:
            return set()
        try:
            return {
                int(value.strip())
                for value in self.telegram_allowed_user_ids.split(",")
                if value.strip()
            }
        except ValueError as exc:
            raise ValueError("TELEGRAM_ALLOWED_USER_IDS must contain comma-separated numeric IDs.") from exc


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
