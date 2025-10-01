import sys
from pathlib import Path
from datetime import datetime
from sqlmodel import Session, select, delete

# Add project root to PYTHONPATH
project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from db.models import Book, BookSnapshot, Category, ProductType, Tax
from db.database import engine


class SQLPipeline:
    """Pipeline to store scraped books with snapshots and automatic purge of oldest snapshots."""

    MAX_SNAPSHOTS_TO_KEEP = 5  # Keep latest 5 snapshots

    def __init__(self):
        self.seen_upcs = set()
        self.categories_cache = {}
        self.product_types_cache = {}
        self.taxes_cache = {}

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
            spider.logger.info(f"Duplicate UPC in current run skipped: {upc}")
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

            # --- Book / Snapshot ---
            existing_book = session.exec(select(Book).where(Book.upc == upc)).first()
            if existing_book:
                # Create snapshot
                snapshot = BookSnapshot(
                    book_id=existing_book.id,
                    scraped_at=datetime.utcnow(),
                    title=existing_book.title,
                    upc=existing_book.upc,
                    price_excl_tax=existing_book.price_excl_tax,
                    price_incl_tax=existing_book.price_incl_tax,
                    availability=existing_book.availability,
                    number_of_reviews=existing_book.number_of_reviews,
                    rating=existing_book.rating,
                    description=existing_book.description,
                    image_url=existing_book.image_url,
                )
                session.add(snapshot)

                # Update book
                existing_book.title = item.get("title", existing_book.title)
                existing_book.price_excl_tax = item.get("price_excl_tax", existing_book.price_excl_tax)
                existing_book.price_incl_tax = item.get("price_incl_tax", existing_book.price_incl_tax)
                existing_book.availability = item.get("availability", existing_book.availability)
                existing_book.number_of_reviews = item.get("number_of_reviews", existing_book.number_of_reviews)
                existing_book.rating = item.get("rating", existing_book.rating)
                existing_book.description = item.get("description", existing_book.description)
                existing_book.image_url = item.get("image_url", existing_book.image_url)
                existing_book.category_id = category_id
                existing_book.product_type_id = product_type_id
                existing_book.tax_id = tax_id

                # --- Purge old snapshots ---
                snapshots = session.exec(
                    select(BookSnapshot)
                    .where(BookSnapshot.book_id == existing_book.id)
                    .order_by(BookSnapshot.scraped_at.desc())
                ).all()
                if len(snapshots) > self.MAX_SNAPSHOTS_TO_KEEP:
                    to_delete = snapshots[self.MAX_SNAPSHOTS_TO_KEEP:]
                    for s in to_delete:
                        session.delete(s)

            else:
                # New book
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
