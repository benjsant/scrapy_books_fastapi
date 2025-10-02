"""
Database models for the Books project.
Defines entities, their attributes, and relationships using SQLModel.
"""

from datetime import datetime, timezone
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship, Column, TEXT


class Category(SQLModel, table=True):
    """
    Represents a book category (e.g., Fiction, Science).
    """
    __tablename__ = "categories"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, max_length=100, nullable=False)

    # Relationships
    books: List["Book"] = Relationship(back_populates="category")


class ProductType(SQLModel, table=True):
    """
    Represents the type of product (e.g., Hardcover, Paperback, eBook).
    """
    __tablename__ = "product_types"

    id: Optional[int] = Field(default=None, primary_key=True)
    type_name: str = Field(unique=True, max_length=50, nullable=False)

    # Relationships
    books: List["Book"] = Relationship(back_populates="product_type")


class Tax(SQLModel, table=True):
    """
    Represents the tax associated with a book.
    """
    __tablename__ = "taxes"

    id: Optional[int] = Field(default=None, primary_key=True)
    amount: float = Field(nullable=False)  # No unique constraint (several books may share the same tax)

    # Relationships
    books: List["Book"] = Relationship(back_populates="tax")


class Book(SQLModel, table=True):
    """
    Represents the current/latest version of a book.
    Contains descriptive and financial information.
    """
    __tablename__ = "books"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=255, nullable=False)
    upc: str = Field(max_length=50, unique=True, index=True, nullable=False)
    price_excl_tax: float = Field(nullable=False)
    price_incl_tax: float = Field(nullable=False)
    availability: int = Field(nullable=False)
    number_of_reviews: int = Field(nullable=False)
    rating: int = Field(default=0, nullable=False)
    description: Optional[str] = Field(default=None, sa_column=Column(TEXT))
    image_url: Optional[str] = Field(default=None)

    # Foreign keys
    category_id: int = Field(foreign_key="categories.id", nullable=False)
    product_type_id: int = Field(foreign_key="product_types.id", nullable=False)
    tax_id: int = Field(foreign_key="taxes.id", nullable=False)

    # Relationships
    category: Category = Relationship(back_populates="books")
    product_type: ProductType = Relationship(back_populates="books")
    tax: Tax = Relationship(back_populates="books")

    # Historical snapshots
    snapshots: List["BookSnapshot"] = Relationship(back_populates="book")


class BookSnapshot(SQLModel, table=True):
    """
    Historical snapshot of a book at a given scrape time.
    Only keeps dynamic and identifying fields.
    """
    __tablename__ = "book_snapshots"

    id: Optional[int] = Field(default=None, primary_key=True)
    book_id: int = Field(foreign_key="books.id", nullable=False)
    scraped_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), index=True, nullable=False
    )

    # Minimal identifying info
    title: str = Field(max_length=255, nullable=False)

    # Dynamic fields worth tracking
    price_excl_tax: float = Field(nullable=False)
    price_incl_tax: float = Field(nullable=False)
    availability: int = Field(nullable=False)
    number_of_reviews: int = Field(nullable=False)
    rating: int = Field(nullable=False)

    # Relationships
    book: Book = Relationship(back_populates="snapshots")