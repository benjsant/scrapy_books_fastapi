# api/crud/books_crud.py
from typing import List, Optional, Type
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from db.database import engine
from db.models import Book, BookSnapshot, Category, ProductType, Tax
from api.schemas.book import BookSchema
from api.schemas.book import BookSnapshotSchema


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
        return [BookSchema.model_validate(book, from_attributes=True) for book in books]


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
        return [BookSchema.model_validate(book, from_attributes=True) for book in books]


def get_book_by_id(book_id: int) -> Optional[BookSchema]:
    """Return a single book by ID with all relations."""
    with Session(engine) as session:
        statement = select(Book).where(Book.id == book_id).options(
            selectinload(Book.category),
            selectinload(Book.product_type),
            selectinload(Book.tax)
        )
        book = session.exec(statement).first()
        return BookSchema.model_validate(book, from_attributes=True) if book else None


def get_table_data(table_class: Type) -> List:
    """Return all rows from a given table class."""
    with Session(engine) as session:
        statement = select(table_class)
        return session.exec(statement).all()


def get_book_history(book_id: int) -> List[BookSnapshotSchema]:
    """
    Return all historical snapshots for a given book, ordered by scrape date descending.
    """
    with Session(engine) as session:
        statement = (
            select(BookSnapshot)
            .where(BookSnapshot.book_id == book_id)
            .order_by(BookSnapshot.scraped_at.desc())
        )
        snapshots = session.exec(statement).all()
        return [BookSnapshotSchema.model_validate(s, from_attributes=True) for s in snapshots]
    
    