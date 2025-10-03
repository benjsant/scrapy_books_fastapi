"""
Utility functions for formatting API responses.
"""

from typing import List, Any, Dict, Optional
from datetime import datetime, timezone


def format_books(
    books: List[Any],
    fields: Optional[List[str]] = None,
    flatten: bool = True,
) -> List[Dict[str, Any]]:
    """Format list of BookSchema objects into dictionaries, optionally flattening 
    nested relations."""
    formatted_books = []

    for book in books:
        book_dict = book.dict()

        if flatten:
            flattened_dict = {}
            for key, value in book_dict.items():
                if isinstance(value, dict) and key in ["category", "product_type", "tax"]:
                    for k, v in value.items():
                        flattened_dict[f"{key}_{k}"] = v
                else:
                    flattened_dict[key] = value
            book_dict = flattened_dict

        if fields:
            book_dict = {field: book_dict[field] for field in fields if field in book_dict}

        formatted_books.append(book_dict)

    return formatted_books


def format_datetime(dt: datetime) -> str:
    """Format datetime into ISO 8601 string in UTC."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
