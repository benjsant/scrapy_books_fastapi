"""
Pydantic schemas for Book, Category, ProductType, Tax, and BookSnapshot.
"""

from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, field_serializer
from ..utils.formatter import format_datetime


class CategorySchema(BaseModel):
    """Schema representing a book category."""
    id: int
    name: str

    model_config = {"from_attributes": True}


class ProductTypeSchema(BaseModel):
    """Schema representing a product type."""
    id: int
    type_name: str

    model_config = {"from_attributes": True}


class TaxSchema(BaseModel):
    """Schema representing tax information."""
    id: int
    amount: float

    model_config = {"from_attributes": True}


class BookSchema(BaseModel):
    """Schema representing a book with all related details."""
    id: int
    title: str
    upc: str
    price_excl_tax: float
    price_incl_tax: float
    availability: int
    number_of_reviews: int
    rating: int
    description: Optional[str] = None
    image_url: Optional[str] = None
    category: CategorySchema
    product_type: ProductTypeSchema
    tax: TaxSchema

    model_config = {"from_attributes": True}


class BookCreateSchema(BaseModel):
    """Schema for creating a new book."""
    title: str
    upc: str
    price_excl_tax: float
    price_incl_tax: float
    availability: int
    number_of_reviews: int
    rating: int
    description: Optional[str] = None
    image_url: Optional[str] = None
    category_id: int
    product_type_id: int
    tax_id: int


class BookSnapshotSchema(BaseModel):
    """
    Schema representing a snapshot of a scraped book at a given time.
    """

    id: int
    book_id: int
    scraped_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the book was scraped",
    )
    title: str
    price_excl_tax: float
    price_incl_tax: float
    availability: int
    number_of_reviews: int
    rating: int

    model_config = {"from_attributes": True}

    @field_serializer("scraped_at")
    def serialize_scraped_at(self, value: datetime) -> str:
        """Serialize scraped_at using the shared datetime formatter."""
        return format_datetime(value)
