"""
File validation utilities for uploaded images.

Validates file size, MIME type, and image integrity before processing.
"""

from __future__ import annotations

import logging
from io import BytesIO
from PIL import Image
from fastapi import UploadFile, HTTPException

from .config import get_settings

logger = logging.getLogger(__name__)


async def validate_image(file: UploadFile) -> bytes:
    """
    Validate an uploaded image file.

    Checks file size, MIME type, and verifies the image is not corrupted.

    Args:
        file: The uploaded file from FastAPI

    Returns:
        bytes: The validated file contents

    Raises:
        HTTPException: 413 if file too large, 415 if wrong type, 400 if corrupted
    """
    settings = get_settings()

    # Check file size (if provided by the upload client)
    # Multiply MB by 1024*1024 to get bytes
    if file.size and file.size > settings.max_file_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {settings.max_file_size_mb}MB",
        )

    # Verify MIME type matches allowed types
    if file.content_type not in settings.allowed_mime_types:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type. Allowed: {', '.join(settings.allowed_mime_types)}",
        )

    try:
        # Read file contents from the upload stream
        contents = await file.read()
        # Verify the file is a valid image by opening it with PIL
        # .verify() checks the file structure without fully decoding
        Image.open(BytesIO(contents)).verify()
        return contents
    except Exception as e:
        # Log the specific error for debugging
        logger.error(f"Image validation failed: {e}")
        raise HTTPException(status_code=400, detail="Invalid or corrupted image file")
