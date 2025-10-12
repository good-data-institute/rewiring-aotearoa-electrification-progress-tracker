"""Configuration management using Pydantic Settings."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Project-wide settings loaded from .env file."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Data directories
    data_dir: Path = Path("./data")
    bronze_dir: Path = Path("./data/bronze")
    silver_dir: Path = Path("./data/silver")
    gold_dir: Path = Path("./data/gold")

    # API settings
    api_timeout: int = 30
    api_retry_attempts: int = 3

    # Backend settings
    backend_host: str = "localhost"
    backend_port: int = 8000

    # Frontend settings
    streamlit_port: int = 8501
    shiny_port: int = 8502

    def __init__(self, **kwargs):
        """Initialize settings and create data directories."""
        super().__init__(**kwargs)
        self._create_directories()

    def _create_directories(self) -> None:
        """Create data directories if they don't exist."""
        for directory in [self.data_dir, self.bronze_dir, self.silver_dir, self.gold_dir]:
            directory.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
