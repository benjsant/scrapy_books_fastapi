"""
CRUD operations for Book and related models.
"""

from typing import List, Optional, Type
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from db.database import engine
from db.models import Book, Category
from api.schemas.book import BookSchema


def get_all_books() -> List[BookSchema]:
    """Retrieve all books with related category, product type, and tax."""
    with Session(engine) as session:
        statement = select(Book).options(
            selectinload(Book.category),
            selectinload(Book.product_type),
            selectinload(Book.tax),
        )
        books = session.exec(statement).all()
        return [BookSchema.model_validate(book, from_attributes=True) for book in books]


def get_all_categories() -> list[Category]:
    """Return all categories."""
    with Session(engine) as session:
        statement = select(Category)
        return session.exec(statement).all()


def get_books_with_category(category_id: Optional[int] = None) -> List[BookSchema]:
    """Retrieve books filtered by category ID if provided."""
    with Session(engine) as session:
        statement = select(Book).options(
            selectinload(Book.category),
            selectinload(Book.product_type),
            selectinload(Book.tax),
        )
        if category_id is not None:
            statement = statement.where(Book.category_id == category_id)
        books = session.exec(statement).all()
        return [BookSchema.model_validate(book, from_attributes=True) for book in books]


def get_books_by_category_name(category_name: str) -> List[BookSchema]:
    """Retrieve books filtered by category name (fuzzy search)."""
    with Session(engine) as session:
        statement = (
            select(Book)
            .join(Category)
            .where(Category.name.ilike(f"%{category_name}%"))
            .options(
                selectinload(Book.category),
                selectinload(Book.product_type),
                selectinload(Book.tax),
            )
        )
        books = session.exec(statement).all()
        return [BookSchema.model_validate(book, from_attributes=True) for book in books]


def get_books_by_title(title: str) -> List[BookSchema]:
    """Retrieve books using fuzzy search on title."""
    with Session(engine) as session:
        statement = (
            select(Book)
            .where(Book.title.ilike(f"%{title}%"))
            .options(
                selectinload(Book.category),
                selectinload(Book.product_type),
                selectinload(Book.tax),
            )
        )
        books = session.exec(statement).all()
        return [BookSchema.model_validate(book, from_attributes=True) for book in books]


def get_books_by_rating(min_rating: float = 0, max_rating: float = 5) -> List[BookSchema]:
    """Retrieve books filtered by rating range."""
    with Session(engine) as session:
        statement = (
            select(Book)
            .where(Book.rating >= min_rating, Book.rating <= max_rating)
            .options(
                selectinload(Book.category),
                selectinload(Book.product_type),
                selectinload(Book.tax),
            )
        )
        books = session.exec(statement).all()
        return [BookSchema.model_validate(book, from_attributes=True) for book in books]


def get_book_by_id(book_id: int) -> Optional[BookSchema]:
    """Retrieve a single book by its ID along with related category, product type, and tax."""
    with Session(engine) as session:
        statement = select(Book).where(Book.id == book_id).options(
            selectinload(Book.category),
            selectinload(Book.product_type),
            selectinload(Book.tax),
        )
        book = session.exec(statement).first()
        return BookSchema.model_validate(book, from_attributes=True) if book else None


def get_table_data(table_class: Type) -> List:
    """Return all rows from a given table class."""
    with Session(engine) as session:
        return session.exec(select(table_class)).all()
