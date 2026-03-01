"""
Fine-tune YOLO classification model on the sky atmosphere dataset.
"""

import argparse
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Paths relative to the server root (parent of src/app)
DATASET_PATH = (
    Path(__file__).parent.parent.parent / "assets" / "dataset" / "images" / "train"
)
MODEL_OUTPUT_DIR = Path(__file__).parent.parent / "models"
MODEL_OUTPUT_NAME = "sky_classifier"


def main():
    parser = argparse.ArgumentParser(description="Fine-tune YOLO classification model")
    parser.add_argument(
        "--epochs", type=int, default=30, help="Number of training epochs"
    )
    parser.add_argument(
        "--imgsz", type=int, default=224, help="Image size for training"
    )
    parser.add_argument("--batch", type=int, default=8, help="Batch size")
    args = parser.parse_args()

    try:
        from ultralytics import YOLO
    except ImportError:
        logger.error("ultralytics not installed. Run: pip install ultralytics")
        sys.exit(1)

    if not DATASET_PATH.exists():
        logger.error(f"Dataset not found at {DATASET_PATH}")
        sys.exit(1)

    MODEL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    model_path = MODEL_OUTPUT_DIR / f"{MODEL_OUTPUT_NAME}.pt"

    logger.info(f"Loading base model: yolov8n-cls")
    model = YOLO("yolov8n-cls.pt")

    logger.info(f"Starting training on dataset: {DATASET_PATH}")
    logger.info(f"Epochs: {args.epochs}, Image size: {args.imgsz}, Batch: {args.batch}")

    results = model.train(
        data=str(DATASET_PATH),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        project=str(MODEL_OUTPUT_DIR),
        name=MODEL_OUTPUT_NAME,
        exist_ok=True,
        verbose=True,
    )

    best_model_dir = MODEL_OUTPUT_DIR / MODEL_OUTPUT_NAME / "weights"
    if (best_model_dir / "best.pt").exists():
        import shutil

        shutil.copy(best_model_dir / "best.pt", model_path)
        logger.info(f"Model saved to: {model_path}")
    else:
        logger.error("Training completed but best.pt not found")
        sys.exit(1)

    logger.info("Training complete!")


if __name__ == "__main__":
    main()
