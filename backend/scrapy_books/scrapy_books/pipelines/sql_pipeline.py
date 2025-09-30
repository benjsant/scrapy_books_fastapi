import sys
from pathlib import Path
from sqlmodel import Session, select

# Dynamically add project root to PYTHONPATH
project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from db.models import Book, Category, ProductType, Tax
from db.database import engine


class SQLPipeline:
    """Optimized pipeline to store scraped items into PostgreSQL using SQLModel."""

    def __init__(self):
        self.seen_upcs = set()
        self.categories_cache = {}   # name -> id
        self.product_types_cache = {}  # type_name -> id
        self.taxes_cache = {}   # amount -> id

        # Preload existing data in memory
        with Session(engine) as session:
            for cat in session.exec(select(Category)).all():
                self.categories_cache[cat.name] = cat.id
            for ptype in session.exec(select(ProductType)).all():
                self.product_types_cache[ptype.type_name] = ptype.id
            for tax in session.exec(select(Tax)).all():
                self.taxes_cache[tax.amount] = tax.id

    def process_item(self, item, spider):
        upc = item.get("upc")
        if not upc:
            spider.logger.warning("Missing UPC, skipping item")
            return item

        if upc in self.seen_upcs:
            spider.logger.info(f"Duplicate book skipped (in memory): {upc}")
            return item

        with Session(engine) as session:
            # --- Category ---
            cat_name = item.get("category", "Unknown")
            category_id = self.categories_cache.get(cat_name)
            if not category_id:
                category = Category(name=cat_name)
                session.add(category)
                session.flush()
                category_id = category.id
                self.categories_cache[cat_name] = category_id

            # --- ProductType ---
            ptype_name = item.get("product_type", "Unknown")
            product_type_id = self.product_types_cache.get(ptype_name)
            if not product_type_id:
                ptype = ProductType(type_name=ptype_name)
                session.add(ptype)
                session.flush()
                product_type_id = ptype.id
                self.product_types_cache[ptype_name] = product_type_id

            # --- Tax ---
            tax_amount = item.get("tax", 0.0)
            tax_id = self.taxes_cache.get(tax_amount)
            if not tax_id:
                tax = Tax(amount=tax_amount)
                session.add(tax)
                session.flush()
                tax_id = tax.id
                self.taxes_cache[tax_amount] = tax_id

            # --- Book ---
            existing_book = session.exec(select(Book).where(Book.upc == upc)).first()
            if existing_book:
                spider.logger.info(f"Duplicate book skipped (DB): {upc}")
                return item

            book = Book(
                title=item.get("title", "Unknown"),
                upc=upc,
                category_id=category_id,
                product_type_id=product_type_id,
                tax_id=tax_id,
                price_excl_tax=item.get("price_excl_tax", 0.0),
                price_incl_tax=item.get("price_incl_tax", 0.0),
                availability=item.get("availability", 0),
                number_of_reviews=item.get("number_of_reviews", 0),
                rating=item.get("rating", 0),
                description=item.get("description"),
                image_url=item.get("image_url"),
            )
            session.add(book)
            session.commit()

        self.seen_upcs.add(upc)
        return item
