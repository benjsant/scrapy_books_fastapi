# api/routes/books_routes.py
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from api.schemas.book import BookSchema
from api.crud.books_crud import (
    get_all_books,
    get_books_with_category,
    get_book_by_id,
    get_table_data,
)
from db.models import Book, Category, ProductType, Tax
from api.utils.formatter import format_books

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/", response_model=List[BookSchema])
def read_all_books(fields: Optional[List[str]] = Query(None)):
    """Return all books with category, product_type, and tax loaded. Optionally select specific fields."""
    books = get_all_books()
    return format_books(books, fields, flatten=False)


@router.get("/with-category", response_model=List[BookSchema])
def read_books_with_category(category_id: Optional[int] = None, fields: Optional[List[str]] = Query(None)):
    """Return books filtered by category if category_id is provided. Optionally select specific fields."""
    books = get_books_with_category(category_id)
    return format_books(books, fields, flatten=False)


@router.get("/table/{table_name}", response_model=List)
def read_table(table_name: str):
    """Return all rows from a given table by its name."""
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
    fields: Optional[List[str]] = Query(None),
    flatten: bool = True
):
    books = get_all_books()
    return format_books(books, fields=fields, flatten=flatten)

@router.get("/{book_id}", response_model=BookSchema)
def read_book_by_id(book_id: int):
    """Return a single book by id, with all relations loaded."""
    book = get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book
