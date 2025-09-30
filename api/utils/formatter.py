# utils/formatter.py
from typing import List, Any, Dict, Optional
from api.schemas.book import BookSchema

def format_books(
    books: List[BookSchema],
    fields: Optional[List[str]] = None,
    flatten: bool = True
) -> List[Dict[str, Any]]:
    """
    Convert a list of BookSchema objects into dicts.
    Optionally return only specified fields and flatten nested relations.

    :param books: List of BookSchema objects
    :param fields: Optional list of fields to include
    :param flatten: If True, nested objects (category, product_type, tax) are flattened
    :return: List of dictionaries
    """
    formatted_books = []

    for book in books:
        book_dict = book.dict()

        if flatten:
            # Fusionner les relations dans le dictionnaire principal
            flattened_dict = {}
            for key, value in book_dict.items():
                if isinstance(value, dict) and key in ["category", "product_type", "tax"]:
                    for k, v in value.items():
                        flattened_dict[f"{key}_{k}"] = v
                else:
                    flattened_dict[key] = value
            book_dict = flattened_dict

        if fields:
            # Garde uniquement les champs demandés
            book_dict = {field: book_dict[field] for field in fields if field in book_dict}

        formatted_books.append(book_dict)

    return formatted_books
