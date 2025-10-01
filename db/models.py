# db/models.py
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship, Column, TEXT


class Category(SQLModel, table=True):
    __tablename__ = "categories"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, max_length=100)

    # Relationships
    books: list["Book"] = Relationship(back_populates="category")


class ProductType(SQLModel, table=True):
    __tablename__ = "product_types"

    id: int | None = Field(default=None, primary_key=True)
    type_name: str = Field(unique=True, max_length=50)

    # Relationships
    books: list["Book"] = Relationship(back_populates="product_type")


class Tax(SQLModel, table=True):
    __tablename__ = "taxes"

    id: int | None = Field(default=None, primary_key=True)
    amount: float  # retiré unique=True

    # Relationships
    books: list["Book"] = Relationship(back_populates="tax")


class Book(SQLModel, table=True):
    """
    Represents the current/latest version of a book.
    """
    __tablename__ = "books"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=255)
    upc: str = Field(max_length=50, unique=True, index=True)  # garde VARCHAR(50)
    price_excl_tax: float
    price_incl_tax: float
    availability: int
    number_of_reviews: int
    rating: int = Field(default=0)
    description: str | None = Field(default=None, sa_column=Column(TEXT))
    image_url: str | None = Field(default=None)

    # Foreign keys
    category_id: int = Field(foreign_key="categories.id")
    product_type_id: int = Field(foreign_key="product_types.id")
    tax_id: int = Field(foreign_key="taxes.id")

    # Relationships
    category: Category = Relationship(back_populates="books")
    product_type: ProductType = Relationship(back_populates="books")
    tax: Tax = Relationship(back_populates="books")

    # Historical relationship
    snapshots: list["BookSnapshot"] = Relationship(back_populates="book")


class BookSnapshot(SQLModel, table=True):
    """
    Represents a historical snapshot of a book at a given scrape time.
    """
    __tablename__ = "book_snapshots"

    id: int | None = Field(default=None, primary_key=True)
    book_id: int = Field(foreign_key="books.id")
    scraped_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Copy of book attributes at scrape time
    title: str = Field(max_length=255)
    upc: str = Field(max_length=50, index=True)
    price_excl_tax: float
    price_incl_tax: float
    availability: int
    number_of_reviews: int
    rating: int
    description: str | None = Field(default=None, sa_column=Column(TEXT))
    image_url: str | None = Field(default=None)

    # Relationships
    book: Book = Relationship(back_populates="snapshots")
