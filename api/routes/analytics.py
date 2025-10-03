"""
FastAPI routes for analytics endpoints.
"""

from typing import List
from fastapi import APIRouter, HTTPException

from api.schemas.analytics import AveragePricePerCategorySchema, TopCategorySchema
from api.crud.analytics_crud import (
    get_average_book_price,
    get_average_price_per_category,
    get_top_categories_by_book_count,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/average-book-price", response_model=float)
def read_average_book_price() -> float:
    """Return the average price of all books."""
    avg_price = get_average_book_price()
    if avg_price is None:
        raise HTTPException(status_code=404, detail="No books found")
    return avg_price


@router.get(
    "/average-price-per-category", response_model=List[AveragePricePerCategorySchema]
)
def read_average_price_per_category() -> List[AveragePricePerCategorySchema]:
    """Return the average price per category."""
    results = get_average_price_per_category()
    if not results:
        raise HTTPException(status_code=404, detail="No categories found")
    return [AveragePricePerCategorySchema(**r) for r in results]


@router.get("/top-categories", response_model=List[TopCategorySchema])
def read_top_categories(limit: int = 5) -> List[TopCategorySchema]:
    """Return top N categories by book count."""
    results = get_top_categories_by_book_count(limit=limit)
    if not results:
        raise HTTPException(status_code=404, detail="No categories found")
    return [TopCategorySchema(**r) for r in results]
