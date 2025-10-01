# schemas/analytics.py
from pydantic import BaseModel
from typing import Optional

class AveragePricePerCategorySchema(BaseModel):
    category_name: str
    avg_price: float

class TopCategorySchema(BaseModel):
    category_name: str
    book_count: int

class TopExpensiveBookSchema(BaseModel):
    id: int
    title: str
    price_incl_tax: float
    category_name: Optional[str] = None

class TotalTaxPerProductTypeSchema(BaseModel):
    product_type_name: str
    total_tax: float

