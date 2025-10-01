# api/crud/books_crud.py
from typing import List, Optional, Type, Tuple, Dict
from sqlmodel import Session, select, func
from sqlalchemy.orm import selectinload

from db.database import engine
from db.models import Book, Category, ProductType, Tax
from api.schemas.book import BookSchema


# ---------------------------
# CRUD functions
# ---------------------------

def get_all_books() -> List[BookSchema]:
    """Return all books with related category, product_type, and tax."""
    with Session(engine) as session:
        statement = select(Book).options(
            selectinload(Book.category),
            selectinload(Book.product_type),
            selectinload(Book.tax)
        )
        books = session.exec(statement).all()
        return [BookSchema.from_orm(book) for book in books]


def get_books_with_category(category_id: Optional[int] = None) -> List[BookSchema]:
    """Return books filtered by category if provided."""
    with Session(engine) as session:
        statement = select(Book).options(
            selectinload(Book.category),
            selectinload(Book.product_type),
            selectinload(Book.tax)
        )
        if category_id:
            statement = statement.where(Book.category_id == category_id)
        books = session.exec(statement).all()
        return [BookSchema.from_orm(book) for book in books]


def get_book_by_id(book_id: int) -> Optional[BookSchema]:
    """Return a single book by ID with all relations."""
    with Session(engine) as session:
        statement = select(Book).where(Book.id == book_id).options(
            selectinload(Book.category),
            selectinload(Book.product_type),
            selectinload(Book.tax)
        )
        book = session.exec(statement).first()
        return BookSchema.from_orm(book) if book else None


def get_table_data(table_class: Type) -> List:
    """Return all rows from a given table class."""
    with Session(engine) as session:
        statement = select(table_class)
        return session.exec(statement).all()

