from typing import List, Optional, Type, Tuple
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


# ---------------------------
# Analytics functions
# ---------------------------

def get_average_book_price() -> Optional[float]:
    """Return the average price (price_incl_tax) of all books."""
    with Session(engine) as session:
        statement = select(func.avg(Book.price_incl_tax))
        avg_price = session.exec(statement).one()
        return avg_price


def get_average_price_per_category() -> List[dict]:
    """
    Return average price_incl_tax grouped by category.
    Returns a list of dicts: {"category_name": str, "avg_price": float}.
    """
    with Session(engine) as session:
        statement = (
            select(Category.name, func.avg(Book.price_incl_tax))
            .join(Book, Category.id == Book.category_id)
            .group_by(Category.name)
        )
        results = session.exec(statement).all()
        return [{"category_name": name, "avg_price": avg} for name, avg in results]


def get_top_categories_by_book_count(limit: int = 5) -> List[Tuple[str, int]]:
    """
    Return top N categories ordered by book count.
    Returns list of tuples: (category_name, count).
    """
    with Session(engine) as session:
        statement = (
            select(Category.name, func.count(Book.id))
            .join(Book, Category.id == Book.category_id)
            .group_by(Category.name)
            .order_by(func.count(Book.id).desc())
            .limit(limit)
        )
        return session.exec(statement).all()


def get_top_expensive_books(limit: int = 10) -> List[BookSchema]:
    """Return top N most expensive books (by price_incl_tax)."""
    with Session(engine) as session:
        statement = (
            select(Book)
            .order_by(Book.price_incl_tax.desc())
            .limit(limit)
            .options(
                selectinload(Book.category),
                selectinload(Book.product_type),
                selectinload(Book.tax)
            )
        )
        books = session.exec(statement).all()
        return [BookSchema.from_orm(book) for book in books]


def get_total_tax_per_product_type() -> List[Tuple[str, float]]:
    """
    Return total tax grouped by product type.
    Returns list of tuples: (product_type_name, total_tax).
    """
    with Session(engine) as session:
        statement = (
            select(ProductType.type_name, func.sum(Book.price_incl_tax * Tax.amount / 100))
            .join(Book, ProductType.id == Book.product_type_id)
            .join(Tax, Tax.id == Book.tax_id)
            .group_by(ProductType.type_name)
        )
        return session.exec(statement).all()
