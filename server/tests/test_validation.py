"""
Tests for validation utilities.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import HTTPException
from app.utils.validation import validate_image


class TestValidateImage:
    """Tests for validate_image function."""

    @pytest.mark.asyncio
    async def test_valid_jpeg(self, sample_image_bytes):
        """Test validation of valid JPEG image."""
        mock_file = MagicMock()
        mock_file.content_type = "image/jpeg"
        mock_file.size = len(sample_image_bytes)
        mock_file.read = AsyncMock(return_value=sample_image_bytes)

        result = await validate_image(mock_file)
        assert result == sample_image_bytes

    @pytest.mark.asyncio
    async def test_valid_png(self, sample_png_bytes):
        """Test validation of valid PNG image."""
        mock_file = MagicMock()
        mock_file.content_type = "image/png"
        mock_file.size = len(sample_png_bytes)
        mock_file.read = AsyncMock(return_value=sample_png_bytes)

        result = await validate_image(mock_file)
        assert result == sample_png_bytes

    @pytest.mark.asyncio
    @patch("app.utils.validation.get_settings")
    async def test_invalid_file_type(self, mock_settings):
        """Test rejection of invalid file type."""
        mock_settings.return_value.max_file_size_mb = 5
        mock_settings.return_value.allowed_mime_types = ["image/jpeg", "image/png"]

        mock_file = MagicMock()
        mock_file.content_type = "application/pdf"
        mock_file.size = 100

        with pytest.raises(HTTPException) as exc_info:
            await validate_image(mock_file)

        assert exc_info.value.status_code == 415
        assert "Unsupported file type" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_corrupted_image(self, sample_image_bytes):
        """Test rejection of corrupted image."""
        mock_file = MagicMock()
        mock_file.content_type = "image/jpeg"
        mock_file.size = len(sample_image_bytes)
        mock_file.read = AsyncMock(b"not an image")

        with pytest.raises(HTTPException) as exc_info:
            await validate_image(mock_file)

        assert exc_info.value.status_code == 400
