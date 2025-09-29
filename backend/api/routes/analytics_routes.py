from fastapi import APIRouter
from typing import List, Optional
from api.crud import books_crud

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/average-price", response_model=Optional[float])
def get_average_price():
    """Return the average price of all books."""
    return books_crud.get_average_book_price()


@router.get("/average-price-per-category")
def get_average_price_per_category():
    """
    Return the average book price grouped by category.
    Returns: List of tuples (category_name, avg_price).
    """
    return books_crud.get_average_price_per_category()


@router.get("/top-categories")
def get_top_categories(limit: int = 5):
    """
    Return the top N categories ordered by book count.
    Returns: List of tuples (category_name, count).
    """
    return books_crud.get_top_categories_by_book_count(limit)


@router.get("/top-expensive-books")
def get_top_expensive_books(limit: int = 10):
    """
    Return the top N most expensive books with relations.
    """
    return books_crud.get_top_expensive_books(limit)


@router.get("/total-tax-per-product-type")
def get_total_tax_per_product_type():
    """
    Return total taxes grouped by product type.
    Returns: List of tuples (product_type_name, total_tax).
    """
    return books_crud.get_total_tax_per_product_type()
