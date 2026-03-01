"""
Taxonomy mapping layer for converting YOLO predictions to required labels.

The pretrained YOLO model outputs ImageNet-style class names (e.g., "cock", "junco").
This module maps those raw predictions to our required atmospheric phenomenon labels.

Fallback strategy (4 levels):
1. Primary taxonomy mapping
2. Keyword-based secondary mapping (heuristic)
3. Brightness-based heuristic
4. Default fallback
"""

from __future__ import annotations

import logging
from enum import Enum
from io import BytesIO
from typing import Any, Optional
from pydantic import BaseModel
from PIL import Image

from ..utils.config import get_settings

logger = logging.getLogger(__name__)


class FallbackMethod(str, Enum):
    """Method used to determine the prediction."""

    PRIMARY = "primary"
    HEURISTIC = "heuristic"
    BRIGHTNESS = "brightness"
    RAW = "raw"
    DEFAULT = "default"


class TaxonomyResult(BaseModel):
    """Result from taxonomy mapping."""

    predictions: list[dict[str, Any]]
    fallback_method: FallbackMethod


class TaxonomyConfig(BaseModel):
    """Configuration for taxonomy mapping."""

    required_labels: set[str] = {
        "clear_sky",
        "clouds",
        "sunset_sunrise",
        "night_sky_stars",
        "fog_mist_haze",
        "rainbow_lightning",
    }

    label_keywords: dict[str, str] = {
        "clear_sky": "clear_sky",
        "clouds": "clouds",
        "sunset_sunrise": "sunset_sunrise",
        "night_sky_stars": "night_sky_stars",
        "fog_mist_haze": "fog_mist_haze",
        "rainbow_lightning": "rainbow_lightning",
        "clear": "clear_sky",
        "sunny": "clear_sky",
        "cloud": "clouds",
        "overcast": "clouds",
        "cumulus": "clouds",
        "stratus": "clouds",
        "cirrus": "clouds",
        "nimbus": "clouds",
        "sunset": "sunset_sunrise",
        "sunrise": "sunset_sunrise",
        "dawn": "sunset_sunrise",
        "dusk": "sunset_sunrise",
        "twilight": "sunset_sunrise",
        "night": "night_sky_stars",
        "star": "night_sky_stars",
        "galaxy": "night_sky_stars",
        "milky": "night_sky_stars",
        "fog": "fog_mist_haze",
        "mist": "fog_mist_haze",
        "haze": "fog_mist_haze",
        "foggy": "fog_mist_haze",
        "rainbow": "rainbow_lightning",
        "lightning": "rainbow_lightning",
        "storm": "rainbow_lightning",
        "thunder": "rainbow_lightning",
    }

    heuristic_keywords: dict[str, str] = {
        "sky": "clouds",
        "bird": "clear_sky",
        "duck": "clear_sky",
        "goose": "clear_sky",
        "swan": "clear_sky",
        "hawk": "clear_sky",
        "eagle": "clear_sky",
        "owl": "night_sky_stars",
        "bat": "night_sky_stars",
        "poncho": "rainbow_lightning",
        "umbrella": "rainbow_lightning",
        "lighthouse": "clear_sky",
        "castle": "clouds",
        "bridge": "clouds",
        "palace": "clouds",
    }

    brightness_thresholds: dict[str, float] = {
        "night_sky_stars": 40.0,
        "fog_mist_haze": 90.0,
    }

    default_fallback: str = "clear_sky"
    fallback_confidence: float = 0.3


class TaxonomyMapper:
    """
    Maps raw YOLO predictions to taxonomy labels with confidence filtering.
    """

    _instance: TaxonomyMapper | None = None

    def __new__(cls) -> TaxonomyMapper:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._config = TaxonomyConfig()
        self._threshold = get_settings().confidence_threshold
        self._initialized = True

    def normalize_label(self, raw_label: str) -> Optional[str]:
        """Convert a raw YOLO class name to a taxonomy label."""
        raw_lower = raw_label.lower().replace("_", " ").replace("-", " ")
        for keyword, mapped_label in self._config.label_keywords.items():
            if keyword in raw_lower:
                return mapped_label
        return None

    def heuristic_normalize(self, raw_label: str) -> Optional[str]:
        """Heuristic-based label normalization for unexpected YOLO outputs."""
        raw_lower = raw_label.lower().replace("_", " ").replace("-", " ")
        for keyword, mapped_label in self._config.heuristic_keywords.items():
            if keyword in raw_lower:
                return mapped_label
        return None

    def estimate_brightness(self, image_bytes: bytes) -> Optional[float]:
        """Estimate image brightness (0-255). Returns None if unable to process."""
        try:
            img = Image.open(BytesIO(image_bytes)).convert("L")
            pixel = img.getpixel((img.width // 2, img.height // 2))
            if isinstance(pixel, tuple):
                return float(pixel[0])
            return float(pixel) if pixel is not None else None
        except Exception as e:
            logger.warning(f"Failed to estimate brightness: {e}")
            return None

    def brightness_fallback(self, image_bytes: bytes) -> list[dict[str, Any]]:
        """Level 3: Brightness-based fallback heuristic."""
        brightness = self.estimate_brightness(image_bytes)
        if brightness is None:
            return [
                {
                    "label": self._config.default_fallback,
                    "confidence": self._config.fallback_confidence,
                }
            ]

        if brightness < self._config.brightness_thresholds["night_sky_stars"]:
            label = "night_sky_stars"
        elif brightness < self._config.brightness_thresholds["fog_mist_haze"]:
            label = "fog_mist_haze"
        elif brightness < 150:
            label = "sunset_sunrise"
        else:
            label = "clouds"

        return [{"label": label, "confidence": self._config.fallback_confidence}]

    def map_predictions(
        self, raw_predictions: list[tuple[str, float]], image_bytes: bytes | None = None
    ) -> TaxonomyResult:
        """Map raw YOLO predictions to taxonomy predictions with 4-level fallback."""

        # Level 1: Primary taxonomy mapping
        mapped: dict[str, float] = {}
        for label, confidence in raw_predictions:
            normalized = self.normalize_label(label)
            if normalized and normalized in self._config.required_labels:
                if normalized not in mapped or confidence > mapped[normalized]:
                    mapped[normalized] = confidence

        results = [
            {"label": label, "confidence": round(conf, 2)}
            for label, conf in mapped.items()
            if conf >= self._threshold
        ]
        results = sorted(results, key=lambda x: x["confidence"], reverse=True)

        if results:
            return TaxonomyResult(
                predictions=results, fallback_method=FallbackMethod.PRIMARY
            )

        # Level 2: Keyword-based secondary mapping (heuristic)
        mapped_heuristic: dict[str, float] = {}
        for label, confidence in raw_predictions:
            normalized = self.heuristic_normalize(label)
            if normalized and normalized in self._config.required_labels:
                if (
                    normalized not in mapped_heuristic
                    or confidence > mapped_heuristic[normalized]
                ):
                    mapped_heuristic[normalized] = confidence

        results = [
            {"label": label, "confidence": round(conf, 2)}
            for label, conf in mapped_heuristic.items()
            if conf >= self._threshold
        ]
        results = sorted(results, key=lambda x: x["confidence"], reverse=True)

        if results:
            return TaxonomyResult(
                predictions=results, fallback_method=FallbackMethod.HEURISTIC
            )

        # Level 3: Brightness-based heuristic (if image provided)
        if image_bytes:
            results = self.brightness_fallback(image_bytes)
            return TaxonomyResult(
                predictions=results, fallback_method=FallbackMethod.BRIGHTNESS
            )

        # Level 4: Raw predictions fallback
        results = [
            {"label": label, "confidence": round(conf, 2)}
            for label, conf in raw_predictions
            if conf >= self._threshold
        ]
        results = sorted(results, key=lambda x: x["confidence"], reverse=True)

        if results:
            return TaxonomyResult(
                predictions=results, fallback_method=FallbackMethod.RAW
            )

        # Ultimate fallback: default label
        return TaxonomyResult(
            predictions=[
                {
                    "label": self._config.default_fallback,
                    "confidence": self._config.fallback_confidence,
                }
            ],
            fallback_method=FallbackMethod.DEFAULT,
        )


def get_mapper() -> TaxonomyMapper:
    """Get the singleton TaxonomyMapper instance."""
    return TaxonomyMapper()
