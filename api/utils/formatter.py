"""
Utility functions for formatting API responses.

This module provides helpers to format book data and
datetime values consistently across the API.
"""

from typing import List, Any, Dict, Optional
from datetime import datetime, timezone


def format_books(
    books: List[Any],
    fields: Optional[List[str]] = None,
    flatten: bool = True
) -> List[Dict[str, Any]]:
    """
    Convert a list of BookSchema objects into dicts.
    Optionally return only specified fields and flatten nested relations.

    Args:
        books (List[Any]): List of BookSchema objects.
        fields (Optional[List[str]]): Fields to keep in the output.
        flatten (bool): If True, nested objects (category, product_type, tax) are flattened.

    Returns:
        List[Dict[str, Any]]: List of formatted dictionaries.
    """
    formatted_books = []

    for book in books:
        book_dict = book.dict()

        if flatten:
            # Merge nested relations into the main dictionary
            flattened_dict = {}
            for key, value in book_dict.items():
                if isinstance(value, dict) and key in ["category", "product_type", "tax"]:
                    for k, v in value.items():
                        flattened_dict[f"{key}_{k}"] = v
                else:
                    flattened_dict[key] = value
            book_dict = flattened_dict

        if fields:
            # Keep only requested fields
            book_dict = {field: book_dict[field] for field in fields if field in book_dict}

        formatted_books.append(book_dict)

    return formatted_books


def format_datetime(dt: datetime) -> str:
    """
    Format a datetime object into an ISO 8601 string in UTC.

    Args:
        dt (datetime): A datetime object (naive or timezone-aware).

    Returns:
        str: ISO 8601 formatted datetime string in UTC with 'Z' suffix.
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)

    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
