from typing import List
from sqlmodel import Session, select, func
from db.database import engine
from db.models import Book, Category

# ---------------------------
# CRUD / Analytics functions
# ---------------------------

def get_average_book_price() -> float | None:
    """Return the average price_incl_tax of all books."""
    with Session(engine) as session:
        avg_price = session.exec(select(func.avg(Book.price_incl_tax))).one()
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

def get_top_categories_by_book_count(limit: int = 5) -> List[dict]:
    """
    Return top N categories ordered by book count.
    Returns a list of dicts: {"category_name": str, "book_count": int}.
    """
    with Session(engine) as session:
        statement = (
            select(Category.name, func.count(Book.id))
            .join(Book, Category.id == Book.category_id)
            .group_by(Category.name)
            .order_by(func.count(Book.id).desc())
            .limit(limit)
        )
        results = session.exec(statement).all()
        return [{"category_name": name, "book_count": count} for name, count in results]
