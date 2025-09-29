from pydantic import BaseModel
from typing import Optional

class CategorySchema(BaseModel):
    id: int
    name: str
    model_config = {"from_attributes": True}

class ProductTypeSchema(BaseModel):
    id: int
    type_name: str
    model_config = {"from_attributes": True}

class TaxSchema(BaseModel):
    id: int
    amount: float
    model_config = {"from_attributes": True}

class BookSchema(BaseModel):
    id: int
    title: str
    upc: str
    price_excl_tax: float
    price_incl_tax: float
    availability: int
    number_of_reviews: int
    rating: int
    description: Optional[str]
    image_url: Optional[str]
    category: CategorySchema
    product_type: ProductTypeSchema
    tax: TaxSchema
    model_config = {"from_attributes": True}

class BookCreateSchema(BaseModel):
    title: str
    upc: str
    price_excl_tax: float
    price_incl_tax: float
    availability: int
    number_of_reviews: int
    rating: int
    description: Optional[str]
    image_url: Optional[str]
    category_id: int
    product_type_id: int
    tax_id: int
