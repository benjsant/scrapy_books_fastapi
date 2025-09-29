# api/crud/analytics_crud.py
from typing import List
from sqlmodel import Session, select, func
from sqlalchemy.orm import selectinload

from db.database import engine
from db.models import Book, Category, ProductType, Tax
from api.schemas.analytics import (
    AveragePriceSchema,
    CategoryAvgPriceSchema,
    CategoryCountSchema,
    TopExpensiveBookSchema,
    ProductTypeTaxSchema
)

def get_average_book_price() -> AveragePriceSchema:
    """Return the average price of all books."""
    with Session(engine) as session:
        statement = select(func.avg(Book.price_incl_tax))
        avg_price = session.exec(statement).one()
        return AveragePriceSchema(average_price=avg_price or 0.0)

def get_average_price_per_category() -> List[CategoryAvgPriceSchema]:
    """Return average price grouped by category."""
    with Session(engine) as session:
        statement = (
            select(Category.name, func.avg(Book.price_incl_tax))
            .join(Book, Category.id == Book.category_id)
            .group_by(Category.name)
        )
        results = session.exec(statement).all()
        return [
            CategoryAvgPriceSchema(category_name=name, avg_price=avg)
            for name, avg in results
        ]

def get_top_categories_by_book_count(limit: int = 5) -> List[CategoryCountSchema]:
    """Return top categories ordered by book count."""
    with Session(engine) as session:
        statement = (
            select(Category.name, func.count(Book.id))
            .join(Book, Category.id == Book.category_id)
            .group_by(Category.name)
            .order_by(func.count(Book.id).desc())
            .limit(limit)
        )
        results = session.exec(statement).all()
        return [
            CategoryCountSchema(category_name=name, book_count=count)
            for name, count in results
        ]

def get_top_expensive_books(limit: int = 10) -> List[TopExpensiveBookSchema]:
    """Return the top N most expensive books."""
    with Session(engine) as session:
        statement = (
            select(Book)
            .order_by(Book.price_incl_tax.desc())
            .limit(limit)
            .options(
                selectinload(Book.category),
                selectinload(Book.product_type),
                selectinload(Book.tax)
            )
        )
        results = session.exec(statement).all()
        return [
            TopExpensiveBookSchema(
                id=book.id,
                title=book.title,
                price_incl_tax=book.price_incl_tax
            )
            for book in results
        ]

def get_total_tax_per_product_type() -> List[ProductTypeTaxSchema]:
    """Return total taxes grouped by product type."""
    with Session(engine) as session:
        statement = (
            select(ProductType.type_name, func.sum(Book.price_incl_tax * Tax.amount / 100))
            .join(Book, ProductType.id == Book.product_type_id)
            .join(Tax, Tax.id == Book.tax_id)
            .group_by(ProductType.type_name)
        )
        results = session.exec(statement).all()
        return [
            ProductTypeTaxSchema(product_type_name=ptype, total_tax=total)
            for ptype, total in results
        ]
