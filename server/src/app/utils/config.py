"""
Application configuration using Pydantic Settings.

Centralizes all configurable parameters with support for environment variables.
Uses pydantic-settings for automatic .env file loading.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_env_path() -> Path:
    """Get the path to the .env file (server root)."""
    return Path(__file__).parent.parent.parent / ".env"


class Settings(BaseSettings):
    """Application configuration values with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=str(get_env_path()),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    max_file_size_mb: int = Field(
        default=5, description="Maximum upload file size in MB"
    )
    allowed_mime_types: list[str] = Field(
        default=["image/jpeg", "image/png"],
        description="Allowed MIME types for image uploads",
    )
    confidence_threshold: float = Field(
        default=0.1,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold for predictions",
    )
    default_model: str = Field(
        default="yolov8n-cls", description="Default YOLO model to use"
    )
    model_cache_dir: str = Field(
        default="./.models", description="Directory to cache YOLO models"
    )
    log_level: str = Field(default="INFO", description="Logging level")
    cors_origins: list[str] = Field(default=["*"], description="CORS allowed origins")
    uvicorn_timeout_keep_alive: int = Field(
        default=5, description="Uvicorn keep-alive timeout in seconds"
    )
    uvicorn_timeout_grace_period: int = Field(
        default=10, description="Uvicorn graceful shutdown timeout in seconds"
    )

    @field_validator("allowed_mime_types", mode="before")
    @classmethod
    def parse_mime_types(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [x.strip() for x in v.split(",")]
        return v

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [x.strip() for x in v.split(",")]
        return v

    def configure_logging(self) -> None:
        """Configure logging based on settings."""
        numeric_level = getattr(logging, self.log_level.upper(), logging.INFO)
        logging.basicConfig(
            level=numeric_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        logging.getLogger().setLevel(numeric_level)


_settings: Settings | None = None


def get_settings() -> Settings:
    """Get the singleton Settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
        _settings.configure_logging()
    return _settings
