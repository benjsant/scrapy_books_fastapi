"""
Pydantic schemas for analytics endpoints.
"""

from typing import Optional
from pydantic import BaseModel


class AveragePricePerCategorySchema(BaseModel):
    """Schema representing average price grouped by category."""
    category_name: str
    avg_price: float


class TopCategorySchema(BaseModel):
    """Schema representing a top category with book count."""
    category_name: str
    book_count: int


class TopExpensiveBookSchema(BaseModel):
    """Schema representing a top expensive book."""
    id: int
    title: str
    price_incl_tax: float
    category_name: Optional[str] = None


class TotalTaxPerProductTypeSchema(BaseModel):
    """Schema representing total tax aggregated per product type."""
    product_type_name: str
    total_tax: float
