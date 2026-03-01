"""
FastAPI application entry point for Sky Atmosphere Analyzer.

This module configures the FastAPI app, CORS middleware, and defines
the API endpoints for image analysis.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

# Now import FastAPI and other modules
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from .handlers.analyze import analyze_image, save_result
from .handlers.history import router as history_router
from .utils.validation import validate_image
from .utils.config import get_settings
from .models.yolo_model import get_model
from .services.storage import UploadResult

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.

    Startup: Load the YOLO model once when the application starts.
    Shutdown: Clean up resources when the application stops.
    """
    logger.info("Starting up - loading YOLO model...")
    _ = get_model()  # Force model loading at startup
    logger.info("Model loaded, ready to serve")
    yield
    logger.info("Shutting down")


# Create FastAPI application with metadata and lifespan handler
app = FastAPI(
    title="Sky Atmosphere Analyzer API",
    description="YOLO-based atmospheric phenomena classification",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware with configurable origins
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register router for history endpoints
app.include_router(history_router)


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        dict: Simple status indicator
    """
    return {"status": "healthy"}


@app.post("/api/v1/analyze", response_model=UploadResult)
async def analyze(file: UploadFile = File(...)):
    """
    Analyze an uploaded image to detect atmospheric phenomena.
    """
    contents = await validate_image(file)
    filename = file.filename or "unknown.jpg"
    result = await analyze_image(contents=contents, filename=filename)
    stored_result = save_result(
        original_filename=filename,
        group=result.group,
        predictions=result.predictions,
        processing_time_ms=result.processing_time_ms,
        fallback_method=result.fallback_method,
    )
    return stored_result
