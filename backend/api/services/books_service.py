"""
Service layer for Book-related operations.
Contains business logic and calls the CRUD layer.
"""

from typing import List, Type, Optional
from db.models import Book
from api.crud import books_crud


def get_all_books() -> List[Book]:
    """Return all books (delegates to CRUD)."""
    return books_crud.get_all_books()


def get_books_with_category() -> List[Book]:
    """Return all books with their categories (delegates to CRUD)."""
    return books_crud.get_books_with_category()


def get_table_data(table_class: Type) -> List:
    """Return all rows from a given table class (delegates to CRUD)."""
    return books_crud.get_table_data(table_class)


def get_book_by_id(book_id: int) -> Optional[Book]:
    """Return a book by ID (delegates to CRUD)."""
    return books_crud.get_book_by_id(book_id)
