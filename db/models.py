# db/models.py
from sqlmodel import SQLModel, Field, Relationship

class Category(SQLModel, table=True):
    __tablename__ = "category"
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, max_length=100)
    books: list["Book"] = Relationship(back_populates="category")

class ProductType(SQLModel, table=True):
    __tablename__ = "product_type"
    id: int | None = Field(default=None, primary_key=True)
    type_name: str = Field(unique=True, max_length=50)
    books: list["Book"] = Relationship(back_populates="product_type")

class Tax(SQLModel, table=True):
    __tablename__ = "tax"
    id: int | None = Field(default=None, primary_key=True)
    amount: float = Field(unique=True)
    books: list["Book"] = Relationship(back_populates="tax")

class Book(SQLModel, table=True):
    __tablename__ = "book"
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=255)
    upc: str = Field(unique=True, max_length=50)
    price_excl_tax: float
    price_incl_tax: float
    availability: int
    number_of_reviews: int
    rating: int = Field(default=0)
    description: str | None = Field(default=None)
    image_url: str | None = Field(default=None)  # rendre optionnel si parfois absent

    # Foreign keys
    category_id: int = Field(foreign_key="category.id")
    product_type_id: int = Field(foreign_key="product_type.id")
    tax_id: int = Field(foreign_key="tax.id")

    # Relationships
    category: Category = Relationship(back_populates="books")
    product_type: ProductType = Relationship(back_populates="books")
    tax: Tax = Relationship(back_populates="books")
