"""
Database initialization and session management.

This module configures the SQLModel engine using settings, 
handles database initialization, readiness checks, 
and provides a FastAPI dependency for sessions.
"""

import time
from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy.exc import OperationalError
from config.settings import settings
from db.models import Book, Category, ProductType, Tax  # your SQLModel models

# --- Global engine ---
DATABASE_URL = settings.database_url
print(f"[INFO] Using database URL: {DATABASE_URL}")

engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"options": "-c timezone=utc"}
)

# --- Database initialization ---
def init_db(drop_existing: bool = False) -> None:
    """Create all tables in the database."""
    if drop_existing:
        print("[INFO] Dropping existing tables...")
        SQLModel.metadata.drop_all(engine)

    print("[INFO] Creating tables...")
    SQLModel.metadata.create_all(engine)
    print("[INFO] Tables created successfully!")

# --- Wait for PostgreSQL readiness ---
def wait_for_postgres(timeout: int = 30, interval: float = 1.0) -> None:
    """Wait until PostgreSQL is ready to accept connections."""
    start = time.time()
    while True:
        try:
            with engine.connect():
                print("[INFO] PostgreSQL is ready!")
                return
        except OperationalError:
            elapsed = time.time() - start
            if elapsed > timeout:
                raise TimeoutError(f"PostgreSQL did not start in time ({timeout}s)")
            print(f"[INFO] Waiting for PostgreSQL... ({int(elapsed)}s elapsed)")
            time.sleep(interval)

# --- Dependency for FastAPI ---
def get_db():
    """Yield a SQLModel session for FastAPI dependency injection."""
    with Session(engine) as session:
        yield session
