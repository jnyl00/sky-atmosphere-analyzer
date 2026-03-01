"""
Handler for the /api/v1/results endpoint.

Provides retrieval of paginated analysis results stored in memory.
"""

from __future__ import annotations

from typing import List, Dict, Any
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from ..services.storage import get_storage, UploadResult

router = APIRouter()

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


class PaginatedResultsResponse(BaseModel):
    """Paginated response for results endpoint."""

    model_config = {"from_attributes": True}

    results: List[Dict[str, Any]] = Field(description="List of results")
    page: int = Field(ge=1, description="Current page number")
    page_size: int = Field(ge=1, le=MAX_PAGE_SIZE, description="Items per page")
    total: int = Field(ge=0, description="Total number of results")
    total_pages: int = Field(ge=0, description="Total number of pages")


@router.get("/api/v1/results", response_model=PaginatedResultsResponse)
async def get_results(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(
        DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Items per page"
    ),
) -> PaginatedResultsResponse:
    """
    Retrieve paginated past analysis results.
    """
    storage = get_storage()
    all_results = storage.get_all()
    total = len(all_results)
    total_pages = (total + page_size - 1) // page_size

    start = (page - 1) * page_size
    end = start + page_size
    paginated_results = all_results[start:end]

    return PaginatedResultsResponse(
        results=[r.to_dict() for r in paginated_results],
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )
