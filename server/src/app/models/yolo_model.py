"""
YOLO model wrapper providing singleton access to the classification model.

Uses the singleton pattern to ensure the model is loaded only once at startup,
reducing memory usage and inference latency for subsequent requests.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.request import urlretrieve

from ultralytics import YOLO

from ..utils.config import get_settings

if TYPE_CHECKING:
    from typing import Optional

logger = logging.getLogger(__name__)

YOLO_WEIGHTS_BASE_URL = "https://github.com/ultralytics/assets/releases/download/v8.3.0"


class YOLOModel:
    """
    Singleton wrapper for YOLO classification model.
    """

    _instance: Optional[YOLOModel] = None
    _model: Optional[YOLO] = None

    def __new__(cls) -> YOLOModel:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._model is None:
            self._load_model()

    def _download_model(self, model_name: str, cache_dir: Path) -> Path:
        """Download the YOLO model to the custom cache directory if not present."""
        model_file = cache_dir / f"{model_name}.pt"

        if model_file.exists():
            logger.info(f"Model already cached at: {model_file}")
            return model_file

        url = f"{YOLO_WEIGHTS_BASE_URL}/{model_name}.pt"
        logger.info(f"Downloading model from: {url}")

        try:
            urlretrieve(url, model_file)
            logger.info(f"Model downloaded to: {model_file}")
        except Exception as e:
            logger.error(f"Failed to download model: {e}")
            raise

        return model_file

    def _load_model(self) -> None:
        """Load the YOLO classification model from disk."""
        settings = get_settings()
        model_name = settings.default_model

        cache_dir = Path(settings.model_cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Loading YOLO classification model: {model_name}")
        logger.info(f"Model cache directory: {cache_dir}")

        model_path = self._download_model(model_name, cache_dir)
        self._model = YOLO(str(model_path))
        logger.info("Model loaded successfully")

    def predict(self, image_path: str) -> list[tuple[str, float]]:
        """Run classification inference on an image."""
        if self._model is None:
            raise RuntimeError("Model not loaded")

        results = self._model(image_path, verbose=False)

        if not results or not results[0].probs:
            return []

        probs = results[0].probs
        top5 = probs.top5
        confs = probs.data[top5].tolist()
        names = self._model.names

        logger.info(
            f"Raw YOLO predictions: {[(names[i], confs[idx]) for idx, i in enumerate(top5)]}"
        )

        predictions = [(names[i], confs[idx]) for idx, i in enumerate(top5)]
        return predictions


def get_model() -> YOLOModel:
    """Get the singleton YOLO model instance."""
    return YOLOModel()
