"""Configuration management using environment variables."""

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Project-wide settings loaded from .env file."""

    def __init__(self):
        """Initialize settings from environment variables and create data directories."""
        # Data directories
        self.data_dir = Path(os.getenv("DATA_DIR", "./data"))
        self.raw_dir = Path(os.getenv("RAW_DIR", "./data/raw"))
        self.processed_dir = Path(os.getenv("PROCESSED_DIR", "./data/processed"))
        self.metrics_dir = Path(os.getenv("METRICS_DIR", "./data/metrics"))

        # API settings
        self.api_timeout = int(os.getenv("API_TIMEOUT", "60"))
        self.api_retry_attempts = int(os.getenv("API_RETRY_ATTEMPTS", "3"))

        # Backend settings
        self.backend_host = os.getenv("BACKEND_HOST", "localhost")
        self.backend_port = int(os.getenv("BACKEND_PORT", "8000"))

        # Frontend settings
        self.streamlit_port = int(os.getenv("STREAMLIT_PORT", "8501"))
        self.shiny_port = int(os.getenv("SHINY_PORT", "8502"))

        # AWS
        self.bucket_url = os.getenv(
            "BUCKET_URL", "https://your-bucket-name.s3.amazonaws.com"
        )

        # Create directories
        self._create_directories()

    def _create_directories(self) -> None:
        """Create data directories if they don't exist."""
        for directory in [
            self.data_dir,
            self.raw_dir,
            self.processed_dir,
            self.metrics_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
