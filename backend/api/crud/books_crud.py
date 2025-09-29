from typing import List, Optional, Type
from sqlmodel import Session, select
from sqlmodel.sql.expression import Select
from sqlalchemy.orm import selectinload

from db.database import engine
from db.models import Book, Category, ProductType, Tax


def get_all_books() -> List[Book]:
    """Return all books with their related category, product_type, and tax loaded."""
    with Session(engine) as session:
        statement: Select = select(Book).options(
            selectinload(Book.category),
            selectinload(Book.product_type),
            selectinload(Book.tax)
        )
        results = session.exec(statement).all()
        return results


def get_books_with_category(category_id: Optional[int] = None) -> List[Book]:
    """
    Return books filtered by category if category_id is provided.
    Related fields are loaded to avoid DetachedInstanceError.
    """
    with Session(engine) as session:
        statement: Select = select(Book).options(
            selectinload(Book.category),
            selectinload(Book.product_type),
            selectinload(Book.tax)
        )
        if category_id:
            statement = statement.where(Book.category_id == category_id)
        results = session.exec(statement).all()
        return results


def get_book_by_id(book_id: int) -> Optional[Book]:
    """Return a single book by id, with relations loaded."""
    with Session(engine) as session:
        statement: Select = select(Book).where(Book.id == book_id).options(
            selectinload(Book.category),
            selectinload(Book.product_type),
            selectinload(Book.tax)
        )
        book = session.exec(statement).first()
        return book


def get_table_data(table_class: Type) -> List:
    """Return all rows from a given table class."""
    with Session(engine) as session:
        statement: Select = select(table_class)
        results = session.exec(statement).all()
        return results
