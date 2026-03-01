"""
Tests for storage service module.
"""

import pytest
from datetime import datetime, timezone
from app.services.storage import (
    Prediction,
    UploadResult,
    ResultStorage,
    get_storage,
)


class TestPrediction:
    """Tests for Prediction model."""

    def test_prediction_creation(self):
        """Test creating a Prediction."""
        pred = Prediction(label="clouds", confidence=0.85)
        assert pred.label == "clouds"
        assert pred.confidence == 0.85

    def test_prediction_to_dict(self):
        """Test Prediction serialization."""
        pred = Prediction(label="clouds", confidence=0.85)
        result = pred.model_dump()
        assert result == {"label": "clouds", "confidence": 0.85}


class TestUploadResult:
    """Tests for UploadResult model."""

    def test_upload_result_creation(self):
        """Test creating an UploadResult."""
        now = datetime.now(timezone.utc)
        predictions = [
            Prediction(label="clouds", confidence=0.85),
            Prediction(label="clear_sky", confidence=0.45),
        ]
        result = UploadResult(
            id="test-id",
            timestamp=now,
            original_filename="test.jpg",
            group="atmosphere",
            predictions=predictions,
            processing_time_ms=150,
        )
        assert result.id == "test-id"
        assert result.original_filename == "test.jpg"
        assert result.group == "atmosphere"
        assert len(result.predictions) == 2

    def test_upload_result_to_dict(self):
        """Test UploadResult serialization."""
        now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        predictions = [Prediction(label="clouds", confidence=0.85)]
        result = UploadResult(
            id="test-id",
            timestamp=now,
            original_filename="test.jpg",
            group="atmosphere",
            predictions=predictions,
            processing_time_ms=150,
        )
        result_dict = result.to_dict()
        assert result_dict["id"] == "test-id"
        assert result_dict["original_filename"] == "test.jpg"
        assert result_dict["group"] == "atmosphere"
        assert result_dict["processing_time_ms"] == 150
        assert "timestamp" in result_dict
        assert result_dict["predictions"][0]["label"] == "clouds"

    def test_upload_result_with_fallback_method(self):
        """Test UploadResult with fallback_method."""
        now = datetime.now(timezone.utc)
        result = UploadResult(
            id="test-id",
            timestamp=now,
            original_filename="test.jpg",
            group="atmosphere",
            predictions=[Prediction(label="clouds", confidence=0.85)],
            processing_time_ms=150,
            fallback_method="brightness",
        )
        assert result.fallback_method == "brightness"

    def test_upload_result_without_fallback_method(self):
        """Test UploadResult without fallback_method defaults to None."""
        now = datetime.now(timezone.utc)
        result = UploadResult(
            id="test-id",
            timestamp=now,
            original_filename="test.jpg",
            group="atmosphere",
            predictions=[Prediction(label="clouds", confidence=0.85)],
            processing_time_ms=150,
        )
        assert result.fallback_method is None


class TestResultStorage:
    """Tests for ResultStorage."""

    def test_add_result(self):
        """Test adding a result to storage."""
        storage = get_storage()
        storage._results = []  # Reset for test

        result = storage.add(
            original_filename="test.jpg",
            group="atmosphere",
            predictions=[{"label": "clouds", "confidence": 0.85}],
            processing_time_ms=150,
        )

        assert result.original_filename == "test.jpg"
        assert result.group == "atmosphere"
        assert len(result.predictions) == 1
        assert result.predictions[0].label == "clouds"

    def test_add_result_with_fallback(self):
        """Test adding a result with fallback_method."""
        storage = get_storage()
        storage._results = []  # Reset for test

        result = storage.add(
            original_filename="test.jpg",
            group="atmosphere",
            predictions=[{"label": "clouds", "confidence": 0.85}],
            processing_time_ms=150,
            fallback_method="brightness",
        )

        assert result.fallback_method == "brightness"

    def test_get_all_returns_newest_first(self):
        """Test results are returned newest first."""
        storage = get_storage()
        storage._results = []  # Reset for test

        # Add results in order
        storage.add("a.jpg", "atmosphere", [{"label": "a", "confidence": 0.1}], 100)
        storage.add("b.jpg", "atmosphere", [{"label": "b", "confidence": 0.2}], 200)
        storage.add("c.jpg", "atmosphere", [{"label": "c", "confidence": 0.3}], 300)

        results = storage.get_all()

        assert len(results) == 3
        # Newest first means c.jpg should be first
        assert results[0].original_filename == "c.jpg"
        assert results[1].original_filename == "b.jpg"
        assert results[2].original_filename == "a.jpg"

    def test_get_all_empty_storage(self):
        """Test getting all from empty storage."""
        storage = get_storage()
        storage._results = []  # Reset for test

        results = storage.get_all()
        assert results == []


class TestGetStorage:
    """Tests for get_storage function."""

    def test_get_storage_returns_singleton(self):
        """Test get_storage returns the same instance."""
        storage1 = get_storage()
        storage2 = get_storage()
        assert storage1 is storage2
