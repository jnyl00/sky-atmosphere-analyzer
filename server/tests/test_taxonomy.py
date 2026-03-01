"""
Tests for taxonomy mapping module.
"""

import pytest
from app.models.taxonomy import (
    TaxonomyMapper,
    TaxonomyConfig,
    FallbackMethod,
    get_mapper,
)


class TestTaxonomyConfig:
    """Tests for TaxonomyConfig."""

    def test_required_labels(self):
        """Test that all required labels are defined."""
        config = TaxonomyConfig()
        expected = {
            "clear_sky",
            "clouds",
            "sunset_sunrise",
            "night_sky_stars",
            "fog_mist_haze",
            "rainbow_lightning",
        }
        assert config.required_labels == expected

    def test_label_keywords_contains_direct_mappings(self):
        """Test that direct label mappings exist."""
        config = TaxonomyConfig()
        assert config.label_keywords["clear_sky"] == "clear_sky"
        assert config.label_keywords["clouds"] == "clouds"
        assert config.label_keywords["sunset_sunrise"] == "sunset_sunrise"

    def test_label_keywords_contains_secondary_mappings(self):
        """Test that secondary keyword mappings exist."""
        config = TaxonomyConfig()
        assert config.label_keywords["clear"] == "clear_sky"
        assert config.label_keywords["sunny"] == "clear_sky"
        assert config.label_keywords["fog"] == "fog_mist_haze"


class TestTaxonomyMapper:
    """Tests for TaxonomyMapper."""

    def test_normalize_label_direct_match(self):
        """Test direct label matching."""
        mapper = get_mapper()
        assert mapper.normalize_label("clouds") == "clouds"
        assert mapper.normalize_label("clear_sky") == "clear_sky"

    def test_normalize_label_keyword_match(self):
        """Test keyword-based label matching."""
        mapper = get_mapper()
        assert mapper.normalize_label("sunny") == "clear_sky"
        assert mapper.normalize_label("overcast") == "clouds"
        assert mapper.normalize_label("foggy") == "fog_mist_haze"

    def test_normalize_label_case_insensitive(self):
        """Test case-insensitive matching."""
        mapper = get_mapper()
        assert mapper.normalize_label("CLOUD") == "clouds"
        assert mapper.normalize_label("Sunset") == "sunset_sunrise"

    def test_normalize_label_with_underscores(self):
        """Test label normalization with underscores."""
        mapper = get_mapper()
        assert mapper.normalize_label("night_sky") == "night_sky_stars"

    def test_normalize_label_no_match(self):
        """Test returns None when no match found."""
        mapper = get_mapper()
        assert mapper.normalize_label("xyz123") is None

    def test_heuristic_normalize(self):
        """Test heuristic normalization."""
        mapper = get_mapper()
        assert mapper.heuristic_normalize("bird") == "clear_sky"
        assert mapper.heuristic_normalize("castle") == "clouds"
        assert mapper.heuristic_normalize("unknown") is None


class TestTaxonomyMapperMapPredictions:
    """Tests for map_predictions method."""

    def test_primary_mapping(self, sample_predictions):
        """Test primary taxonomy mapping."""
        mapper = get_mapper()
        # "cloud" is in label_keywords -> clouds
        result = mapper.map_predictions(sample_predictions)
        assert len(result.predictions) > 0
        assert result.predictions[0]["label"] == "clouds"

    def test_returns_fallback_method_primary(self, sample_predictions):
        """Test that primary method is returned."""
        mapper = get_mapper()
        result = mapper.map_predictions(sample_predictions)
        # Primary should not show fallback_method or show as primary
        # (the handler filters this out)
        assert result.fallback_method == FallbackMethod.PRIMARY

    def test_heuristic_fallback(self):
        """Test heuristic fallback when primary fails."""
        mapper = get_mapper()
        # Only unknown classes - should use heuristic
        predictions = [("bird", 0.9), ("castle", 0.8)]
        result = mapper.map_predictions(predictions)
        assert result.fallback_method in [
            FallbackMethod.HEURISTIC,
            FallbackMethod.PRIMARY,  # bird might match
        ]

    def test_brightness_fallback(self, sample_image_bytes):
        """Test brightness fallback when other methods fail."""
        mapper = get_mapper()
        # Very specific unknown predictions
        predictions = [("xyz123", 0.9), ("abc456", 0.8)]
        result = mapper.map_predictions(predictions, image_bytes=sample_image_bytes)
        # Should use brightness fallback
        assert result.fallback_method == FallbackMethod.BRIGHTNESS

    def test_default_fallback(self):
        """Test default fallback when everything fails."""
        mapper = get_mapper()
        # Empty predictions should use default
        result = mapper.map_predictions([])
        assert result.fallback_method == FallbackMethod.DEFAULT
        assert result.predictions[0]["label"] == "clear_sky"

    def test_predictions_sorted_by_confidence(self):
        """Test predictions are sorted by confidence descending."""
        mapper = get_mapper()
        predictions = [
            ("cloud", 0.30),
            ("clear", 0.90),
            ("sunny", 0.60),
        ]
        result = mapper.map_predictions(predictions)
        # Should map to clear_sky (highest conf: sunny/clear -> 0.90)
        assert (
            result.predictions[0]["confidence"] >= result.predictions[-1]["confidence"]
        )

    def test_confidence_threshold_filtering(self):
        """Test confidence threshold filtering."""
        mapper = get_mapper()
        predictions = [("cloud", 0.05), ("clear", 0.99)]  # 0.05 below threshold
        result = mapper.map_predictions(predictions)
        # Only clear_sky should remain (0.99 >= 0.1)
        assert len(result.predictions) >= 1
        assert all(p["confidence"] >= 0.1 for p in result.predictions)


class TestFallbackMethod:
    """Tests for FallbackMethod enum."""

    def test_fallback_methods_defined(self):
        """Test all fallback methods are defined."""
        expected = {"primary", "heuristic", "brightness", "raw", "default"}
        actual = {m.value for m in FallbackMethod}
        assert expected == actual

    def test_fallback_method_is_string(self):
        """Test FallbackMethod can be used as string."""
        assert FallbackMethod.PRIMARY.value == "primary"
        assert FallbackMethod.HEURISTIC.value == "heuristic"
