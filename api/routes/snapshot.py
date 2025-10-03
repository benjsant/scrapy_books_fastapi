from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException

from api.schemas.book import BookSnapshotSchema
from api.crud.snapshot_crud import (
    get_snapshots_by_book_id,
    compare_snapshots_price,
    compare_snapshots_rating,
)
from api.utils.formatter import format_books

router = APIRouter(prefix="/snapshots", tags=["snapshots"])


@router.get("/book/{book_id}", response_model=List[BookSnapshotSchema])
def read_snapshots_by_book(book_id: int) -> List[BookSnapshotSchema]:
    """Return all snapshots for a specific book by ID."""
    snapshots = get_snapshots_by_book_id(book_id)
    if not snapshots:
        raise HTTPException(status_code=404, detail="No snapshots found for this book")
    return snapshots


@router.get("/compare-price/{book_id}", response_model=List[Dict[str, Any]])
def compare_price(book_id: int) -> List[Dict[str, Any]]:
    """Return price history of a book (date + price only)."""
    snapshots = compare_snapshots_price(book_id)
    if not snapshots:
        raise HTTPException(status_code=404, detail="No snapshots found to compare prices")
    return snapshots


@router.get("/compare-rating/{book_id}", response_model=List[Dict[str, Any]])
def compare_rating(book_id: int) -> List[Dict[str, Any]]:
    """Return rating history of a book (date + rating only)."""
    snapshots = compare_snapshots_rating(book_id)
    if not snapshots:
        raise HTTPException(status_code=404, detail="No snapshots found to compare ratings")
    return snapshots
