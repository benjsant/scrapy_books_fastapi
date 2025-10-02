from typing import List, Optional, Type
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from db.database import engine
from db.models import Book, BookSnapshot, Category, ProductType, Tax
from api.schemas.book import BookSchema, BookSnapshotSchema


# ---------------------------
# CRUD functions for Books
# ---------------------------

def get_all_books() -> List[BookSchema]:
    """
    Retrieve all books from the database with their related category,
    product type, and tax. Returns a list of BookSchema objects.
    """
    with Session(engine) as session:
        statement = select(Book).options(
            selectinload(Book.category),
            selectinload(Book.product_type),
            selectinload(Book.tax)
        )
        books = session.exec(statement).all()
        return [BookSchema.model_validate(book, from_attributes=True) for book in books]


def get_books_with_category(category_id: Optional[int] = None) -> List[BookSchema]:
    """
    Retrieve books filtered by category if category_id is provided.
    Returns a list of BookSchema objects.
    """
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
    """
    Retrieve a single book by its ID along with related category,
    product type, and tax. Returns a BookSchema object or None if not found.
    """
    with Session(engine) as session:
        statement = select(Book).where(Book.id == book_id).options(
            selectinload(Book.category),
            selectinload(Book.product_type),
            selectinload(Book.tax)
        )
        book = session.exec(statement).first()
        return BookSchema.model_validate(book, from_attributes=True) if book else None


def get_table_data(table_class: Type) -> List:
    """
    Return all rows from a given table class.
    Useful for debugging or administrative purposes.
    """
    with Session(engine) as session:
        statement = select(table_class)
        return session.exec(statement).all()


def get_book_history(book_id: int) -> List[BookSnapshotSchema]:
    """
    Retrieve historical snapshots of a book, ordered by scrape date descending.
    The 'scraped_at' datetime is automatically converted via BookSnapshotSchema
    to the desired timezone/format if a formatter is applied.
    """
    with Session(engine) as session:
        statement = (
            select(BookSnapshot)
            .where(BookSnapshot.book_id == book_id)
            .order_by(BookSnapshot.scraped_at.desc())
        )
        snapshots = session.exec(statement).all()
        return [BookSnapshotSchema.model_validate(s, from_attributes=True) for s in snapshots]
