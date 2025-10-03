"""
CRUD operations for BookSnapshot (historical snapshots of books).
Optimized for per-book analysis: price and rating evolution.
"""

from typing import List, Dict
from sqlmodel import Session, select
from sqlalchemy import func, desc
from db.database import engine
from db.models import Book, BookSnapshot
from api.schemas.book import BookSnapshotSchema


def get_snapshots_by_book_id(book_id: int) -> List[BookSnapshotSchema]:
    """Retrieve all snapshots for a given book_id."""
    with Session(engine) as session:
        snapshots = session.exec(
            select(BookSnapshot)
            .where(BookSnapshot.book_id == book_id)
            .order_by(desc(BookSnapshot.scraped_at))
        ).all()
        return [BookSnapshotSchema.model_validate(s, from_attributes=True) for s in snapshots]


def compare_snapshots_price(book_id: int) -> List[Dict]:
    """
    Return snapshots for a book showing only date + price evolution.
    Sorted by date ascending.
    """
    with Session(engine) as session:
        snapshots = session.exec(
            select(BookSnapshot)
            .where(BookSnapshot.book_id == book_id)
            .order_by(BookSnapshot.scraped_at)
        ).all()
        return [{"scraped_at": s.scraped_at, "price_incl_tax": s.price_incl_tax} for s in snapshots]


def compare_snapshots_rating(book_id: int) -> List[Dict]:
    """
    Return snapshots for a book showing only date + rating evolution.
    Sorted by date ascending.
    """
    with Session(engine) as session:
        snapshots = session.exec(
            select(BookSnapshot)
            .where(BookSnapshot.book_id == book_id)
            .order_by(BookSnapshot.scraped_at)
        ).all()
        return [{"scraped_at": s.scraped_at, "rating": s.rating} for s in snapshots]


def get_price_stats(book_id: int) -> Dict:
    """Get min, max, and avg price_incl_tax for a book's historical snapshots."""
    with Session(engine) as session:
        min_price, max_price, avg_price = session.exec(
            select(
                func.min(BookSnapshot.price_incl_tax),
                func.max(BookSnapshot.price_incl_tax),
                func.avg(BookSnapshot.price_incl_tax)
            ).where(BookSnapshot.book_id == book_id)
        ).one()
        return {"min_price": min_price, "max_price": max_price, "avg_price": avg_price}
