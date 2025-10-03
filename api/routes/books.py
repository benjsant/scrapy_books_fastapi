"""
FastAPI routes for book endpoints.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from db.models import Book, Category, ProductType, Tax
from api.schemas.book import BookSchema
from api.crud.books_crud import (
    get_all_books,
    get_all_categories,
    get_books_by_category_name,
    get_books_with_category,
    get_books_by_title,
    get_books_by_rating,
    get_book_by_id,
    get_table_data,
)
from api.utils.formatter import format_books


router = APIRouter(prefix="/books", tags=["books"])


@router.get("/", response_model=List[BookSchema])
def read_all_books(fields: Optional[List[str]] = Query(None)) -> List[Dict[str, Any]]:
    """Return all books. Optionally select specific fields."""
    books = get_all_books()
    return format_books(books, fields, flatten=False)


@router.get("/categories", response_model=List[Dict[str, Any]])
def read_all_categories() -> List[Dict[str, Any]]:
    """Return all categories available in the database."""
    categories = get_all_categories()
    if not categories:
        raise HTTPException(status_code=404, detail="No categories found")
    return [{"id": c.id, "name": c.name} for c in categories]


@router.get("/with-category", response_model=List[BookSchema])
def read_books_with_category(
    category_id: Optional[int] = None, fields: Optional[List[str]] = Query(None)
) -> List[Dict[str, Any]]:
    """Return books filtered by category ID if provided."""
    books = get_books_with_category(category_id)
    return format_books(books, fields, flatten=False)


@router.get("/search-title", response_model=List[BookSchema])
def search_books_title(title: str = Query(..., min_length=1), fields: Optional[List[str]] = Query(None)) -> List[Dict[str, Any]]:
    """Search books by fuzzy title."""
    books = get_books_by_title(title)
    if not books:
        raise HTTPException(status_code=404, detail="No books match this title")
    return format_books(books, fields=fields, flatten=False)


@router.get("/search-category", response_model=List[BookSchema])
def search_books_category(category_name: str = Query(..., min_length=1), fields: Optional[List[str]] = Query(None)) -> List[Dict[str, Any]]:
    """Search books by fuzzy category name."""
    books = get_books_by_category_name(category_name)
    if not books:
        raise HTTPException(status_code=404, detail="No books found for this category")
    return format_books(books, fields=fields, flatten=False)


@router.get("/search-rating", response_model=List[BookSchema])
def search_books_rating(
    min_rating: float = Query(0, ge=0, le=5),
    max_rating: float = Query(5, ge=0, le=5),
    fields: Optional[List[str]] = Query(None),
) -> List[Dict[str, Any]]:
    """
    Retrieve books filtered by rating range.
    Uses SQL filter via CRUD.
    """
    books = []
    # On récupère tous les ratings possibles et on filtre en Python (alternativement, on pourrait faire un CRUD SQL range)
    for rating in range(int(min_rating*2), int(max_rating*2)+1):  # Convert float range to steps of 0.5 si rating float
        books += get_books_by_rating(rating/2)
    if not books:
        raise HTTPException(status_code=404, detail="No books match this rating range")
    return format_books(books, fields=fields, flatten=False)


@router.get("/table/{table_name}", response_model=List)
def read_table(table_name: str) -> List:
    """Return all rows from a table by its name."""
    table_mapping = {
        "book": Book,
        "category": Category,
        "product_type": ProductType,
        "tax": Tax,
    }
    table_class = table_mapping.get(table_name.lower())
    if not table_class:
        raise HTTPException(status_code=404, detail="Table not found")
    return get_table_data(table_class)


@router.get("/formatted", response_model=List[Dict[str, Any]])
def get_books_formatted(
    fields: Optional[List[str]] = Query(None), flatten: bool = True
) -> List[Dict[str, Any]]:
    """Return books formatted, optionally flattening nested relations."""
    books = get_all_books()
    return format_books(books, fields=fields, flatten=flatten)


@router.get("/{book_id}", response_model=BookSchema)
def read_book_by_id(book_id: int) -> BookSchema:
    """Return a single book by ID with all relations loaded."""
    book = get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book
