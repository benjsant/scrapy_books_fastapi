from fastapi import APIRouter, HTTPException
from typing import List
from api.schemas.book import BookSchema
from api.crud import books_crud
from db.models import Book, Category, ProductType, Tax

router = APIRouter(prefix="/books", tags=["books"])

@router.get("/", response_model=List[BookSchema])
def read_all_books():
    """Return all books with their category, product_type, and tax loaded."""
    return books_crud.get_all_books()

@router.get("/with-category", response_model=List[BookSchema])
def read_books_with_category(category_id: int = None):
    """
    Return books filtered by category if category_id is provided.
    """
    return books_crud.get_books_with_category(category_id)

@router.get("/table/{table_name}", response_model=List)
def read_table(table_name: str):
    """
    Return all rows from a given table by its name.
    """
    table_mapping = {
        "book": Book,
        "category": Category,
        "product_type": ProductType,
        "tax": Tax,
    }
    table_class = table_mapping.get(table_name.lower())
    if not table_class:
        raise HTTPException(status_code=404, detail="Table not found")
    return books_crud.get_table_data(table_class)

@router.get("/{book_id}", response_model=BookSchema)
def read_book_by_id(book_id: int):
    """
    Return a single book by id, with all relations loaded.
    """
    book = books_crud.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book
