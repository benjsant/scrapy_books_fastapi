# scrapy_books/scrapy_books/pipelines/sql_pipeline.py
import sys
from pathlib import Path
from datetime import datetime, timezone
from sqlmodel import Session, select

# Add project root to PYTHONPATH
project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from db.models import Book, BookSnapshot, Category, ProductType, Tax
from db.database import engine


class SQLPipeline:
    """
    Scrapy pipeline to store books in DB, create historical snapshots,
    and purge oldest snapshots beyond MAX_SNAPSHOTS_TO_KEEP.
    """

    MAX_SNAPSHOTS_TO_KEEP = 5  # Keep latest 5 snapshots per book

    def __init__(self):
        self.seen_upcs = set()
        self.categories_cache = {}
        self.product_types_cache = {}
        self.taxes_cache = {}

        # Preload categories, product types, taxes for caching
        with Session(engine) as session:
            for cat in session.exec(select(Category)).all():
                self.categories_cache[cat.name] = cat.id
            for ptype in session.exec(select(ProductType)).all():
                self.product_types_cache[ptype.type_name] = ptype.id
            for tax in session.exec(select(Tax)).all():
                self.taxes_cache[tax.amount] = tax.id

    def process_item(self, item, spider):
        """
        Process a single book item:
        - Skip if UPC missing or already seen in this run
        - Create/update Book and BookSnapshot
        - Purge old snapshots beyond MAX_SNAPSHOTS_TO_KEEP
        """
        upc = item.get("upc")
        if not upc:
            spider.logger.warning("Missing UPC, skipping item")
            return item

        if upc in self.seen_upcs:
            spider.logger.info(f"Duplicate UPC in current run skipped: {upc}")
            return item

        with Session(engine) as session:
            category_id = self._get_or_create_category(session, item.get("category", "Unknown"))
            product_type_id = self._get_or_create_product_type(session, item.get("product_type", "Unknown"))
            tax_id = self._get_or_create_tax(session, item.get("tax", 0.0))

            existing_book = session.exec(select(Book).where(Book.upc == upc)).first()
            if existing_book:
                self._update_book_with_snapshot(session, existing_book, item, category_id, product_type_id, tax_id)
            else:
                self._create_new_book(session, item, upc, category_id, product_type_id, tax_id)

            session.commit()
            self.seen_upcs.add(upc)

        return item

    # -----------------------------
    # Helper Methods
    # -----------------------------
    def _get_or_create_category(self, session: Session, name: str) -> int:
        if name in self.categories_cache:
            return self.categories_cache[name]
        category = Category(name=name)
        session.add(category)
        session.flush()
        self.categories_cache[name] = category.id
        return category.id

    def _get_or_create_product_type(self, session: Session, type_name: str) -> int:
        if type_name in self.product_types_cache:
            return self.product_types_cache[type_name]
        ptype = ProductType(type_name=type_name)
        session.add(ptype)
        session.flush()
        self.product_types_cache[type_name] = ptype.id
        return ptype.id

    def _get_or_create_tax(self, session: Session, amount: float) -> int:
        if amount in self.taxes_cache:
            return self.taxes_cache[amount]
        tax = Tax(amount=amount)
        session.add(tax)
        session.flush()
        self.taxes_cache[amount] = tax.id
        return tax.id

    def _update_book_with_snapshot(self, session: Session, book: Book, item: dict, category_id: int, product_type_id: int, tax_id: int):
        # Create snapshot with latest data
        snapshot = BookSnapshot(
            book_id=book.id,
            scraped_at=datetime.now(timezone.utc),
            title=book.title,
            price_excl_tax=book.price_excl_tax,
            price_incl_tax=book.price_incl_tax,
            availability=book.availability,
            number_of_reviews=book.number_of_reviews,
            rating=book.rating,
        )
        session.add(snapshot)

        # Update main book
        book.title = item.get("title", book.title)
        book.price_excl_tax = item.get("price_excl_tax", book.price_excl_tax)
        book.price_incl_tax = item.get("price_incl_tax", book.price_incl_tax)
        book.availability = item.get("availability", book.availability)
        book.number_of_reviews = item.get("number_of_reviews", book.number_of_reviews)
        book.rating = item.get("rating", book.rating)
        book.description = item.get("description", book.description)
        book.image_url = item.get("image_url", book.image_url)
        book.category_id = category_id
        book.product_type_id = product_type_id
        book.tax_id = tax_id

        # Purge old snapshots
        snapshots = session.exec(
            select(BookSnapshot)
            .where(BookSnapshot.book_id == book.id)
            .order_by(BookSnapshot.scraped_at.desc())
        ).all()
        for old_snap in snapshots[self.MAX_SNAPSHOTS_TO_KEEP:]:
            session.delete(old_snap)

    def _create_new_book(self, session: Session, item: dict, upc: str, category_id: int, product_type_id: int, tax_id: int):
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
