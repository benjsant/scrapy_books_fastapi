from fastapi import APIRouter
from typing import List, Optional, Dict
from api.crud import books_crud

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/average-price", response_model=Optional[float])
def get_average_price():
    """Return the average price of all books."""
    return books_crud.get_average_book_price()


@router.get("/average-price-per-category", response_model=List[Dict[str, float]])
def get_average_price_per_category():
    """
    Return the average book price grouped by category.
    Returns a list of dicts: [{"category": name, "avg_price": value}, ...]
    """
    results = books_crud.get_average_price_per_category()
    # Convert tuples to dicts
    return [{"category": name, "avg_price": avg_price} for name, avg_price in results]


@router.get("/top-categories", response_model=List[Dict[str, int]])
def get_top_categories(limit: int = 5):
    """
    Return the top N categories ordered by book count.
    Returns a list of dicts: [{"category": name, "count": value}, ...]
    """
    results = books_crud.get_top_categories_by_book_count(limit)
    return [{"category": name, "count": count} for name, count in results]


@router.get("/top-expensive-books", response_model=List[Dict])
def get_top_expensive_books(limit: int = 10):
    """
    Return the top N most expensive books.
    Each book is converted to a dict to avoid Pydantic serialization errors.
    """
    books = books_crud.get_top_expensive_books(limit)
    return [book.dict() for book in books]  # Assure que BookSchema ou SQLModel est compatible dict()


@router.get("/total-tax-per-product-type", response_model=List[Dict[str, float]])
def get_total_tax_per_product_type():
    """
    Return total taxes grouped by product type.
    Returns a list of dicts: [{"product_type": name, "total_tax": value}, ...]
    """
    results = books_crud.get_total_tax_per_product_type()
    return [{"product_type": name, "total_tax": total} for name, total in results]
