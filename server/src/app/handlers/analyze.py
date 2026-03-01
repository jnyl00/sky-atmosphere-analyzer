"""
Handler for the /api/analyze endpoint.

Orchestrates the image analysis pipeline: reads uploaded file,
runs YOLO inference, maps results to taxonomy, and returns predictions.
"""

from __future__ import annotations

import logging
import tempfile
import time
from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field

from ..models.yolo_model import get_model
from ..models.taxonomy import get_mapper, TaxonomyResult
from ..services.storage import get_storage, UploadResult


class AnalysisResult(BaseModel):
    """Result from image analysis."""

    group: str = Field(description="Analysis group")
    predictions: list[dict[str, Any]] = Field(
        description="List of predictions with label and confidence"
    )
    processing_time_ms: int = Field(ge=0, description="Processing time in ms")
    fallback_method: str | None = Field(
        default=None, description="Fallback method used if any"
    )


logger = logging.getLogger(__name__)


async def analyze_image(contents: bytes, filename: str) -> AnalysisResult:
    """
    Perform complete image analysis pipeline.

    Takes validated image bytes, saves to temporary file, runs YOLO classification,
    maps raw predictions to taxonomy labels, and returns the results.
    """
    suffix = Path(filename).suffix if filename else ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        start_time = time.perf_counter()

        model = get_model()
        raw_predictions = model.predict(tmp_path)

        mapper = get_mapper()
        taxonomy_result: TaxonomyResult = mapper.map_predictions(
            raw_predictions, image_bytes=contents
        )

        processing_time_ms = int((time.perf_counter() - start_time) * 1000)

        fallback_method = (
            taxonomy_result.fallback_method.value
            if taxonomy_result.fallback_method.value != "primary"
            else None
        )

        return AnalysisResult(
            group="atmosphere",
            predictions=taxonomy_result.predictions,
            processing_time_ms=processing_time_ms,
            fallback_method=fallback_method,
        )
    except Exception:
        raise
    finally:
        try:
            Path(tmp_path).unlink(missing_ok=True)
        except Exception as cleanup_error:
            logger.warning(f"Failed to cleanup temp file {tmp_path}: {cleanup_error}")


def save_result(
    original_filename: str,
    group: str,
    predictions: list[dict[str, Any]],
    processing_time_ms: int,
    fallback_method: str | None = None,
) -> UploadResult:
    """Save analysis result to storage and return the stored result."""
    storage = get_storage()
    result = storage.add(
        original_filename=original_filename,
        group=group,
        predictions=predictions,
        processing_time_ms=processing_time_ms,
        fallback_method=fallback_method,
    )
    return result
