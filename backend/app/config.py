"""
Application Configuration
Centralized configuration management using Pydantic Settings.
Loads database connection, storage directory, and CORS settings from environment variables or defaults.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory for the backend
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent
STORAGE_DIR = PROJECT_ROOT / "storage"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")
    PROJECT_NAME: str = "AI Model Evaluation & Data Reliability Platform"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"

    # Database Configuration (MySQL)
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "adaan")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_NAME: str = os.getenv("DB_NAME", "ai_model_reliability")

    @property
    def DATABASE_URL(self) -> str:
        # Using PyMySQL driver for seamless Python 3.12 MySQL connection
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

    # Storage Paths
    STORAGE_PATH: Path = STORAGE_DIR
    DATASET_STORAGE_PATH: Path = STORAGE_DIR / "datasets"
    MODEL_STORAGE_PATH: Path = STORAGE_DIR / "models"
    REPORT_STORAGE_PATH: Path = STORAGE_DIR / "reports"

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

settings = Settings()

# Ensure storage directories exist at startup
settings.DATASET_STORAGE_PATH.mkdir(parents=True, exist_ok=True)
settings.MODEL_STORAGE_PATH.mkdir(parents=True, exist_ok=True)
settings.REPORT_STORAGE_PATH.mkdir(parents=True, exist_ok=True)
