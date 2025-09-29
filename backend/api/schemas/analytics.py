from pydantic import BaseModel

class AveragePriceSchema(BaseModel):
    average_price: float

class CategoryAvgPriceSchema(BaseModel):
    category_name: str
    avg_price: float

class CategoryCountSchema(BaseModel):
    category_name: str
    book_count: int

class TopExpensiveBookSchema(BaseModel):
    id: int
    title: str
    price_incl_tax: float

class ProductTypeTaxSchema(BaseModel):
    product_type_name: str
    total_tax: float