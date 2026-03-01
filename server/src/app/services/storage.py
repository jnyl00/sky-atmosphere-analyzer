"""
In-memory storage for upload results using Pydantic models.

Stores analysis results with metadata for retrieval via the history endpoint.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, List
from pydantic import BaseModel, Field, ConfigDict


class Prediction(BaseModel):
    """A single prediction with label and confidence."""

    model_config = ConfigDict(populate_by_name=True)

    label: str = Field(description="Predicted label")
    confidence: float = Field(description="Confidence score")


class UploadResult(BaseModel):
    """Represents a single upload analysis result stored in memory."""

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(description="Unique identifier")
    timestamp: datetime = Field(description="Upload timestamp")
    original_filename: str = Field(description="Original uploaded filename")
    group: str = Field(description="Analysis group")
    predictions: List[Prediction] = Field(description="List of predictions")
    processing_time_ms: int = Field(description="Processing time in milliseconds")
    fallback_method: str | None = Field(
        default=None, description="Fallback method used if any"
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "original_filename": self.original_filename,
            "group": self.group,
            "predictions": [p.model_dump() for p in self.predictions],
            "processing_time_ms": self.processing_time_ms,
            "fallback_method": self.fallback_method,
        }


_storage_instance: "ResultStorage | None" = None


class ResultStorage:
    """In-memory storage for upload results using singleton pattern."""

    def __init__(self) -> None:
        self._results: list[UploadResult] = []

    def add(
        self,
        original_filename: str,
        group: str,
        predictions: list[dict[str, Any]],
        processing_time_ms: int,
        fallback_method: str | None = None,
    ) -> UploadResult:
        """Add a new result to storage."""
        result = UploadResult(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            original_filename=original_filename,
            group=group,
            predictions=[Prediction(**p) for p in predictions],
            processing_time_ms=processing_time_ms,
            fallback_method=fallback_method,
        )
        self._results.append(result)
        return result

    def get_all(self) -> list[UploadResult]:
        """Return all stored results, newest first."""
        return list(reversed(self._results))


def get_storage() -> ResultStorage:
    """Get the singleton storage instance."""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = ResultStorage()
    return _storage_instance
