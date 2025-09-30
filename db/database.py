import time
from urllib.parse import quote_plus
from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy.exc import OperationalError
from config.settings import settings
from db.models import Book, Category, ProductType, Tax  # tes modèles SQLModel

# --- Encode password safely to avoid UnicodeDecodeError ---
safe_password = quote_plus(settings.db_password or "")
DATABASE_URL = f"postgresql://{settings.db_user}:{safe_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

# --- Engine global basé sur settings ---
print(f"data: {DATABASE_URL}")
print(f"safe {safe_password}")
engine = create_engine(DATABASE_URL, echo=True, connect_args={"options": "-c timezone=utc"})

# --- Initialisation de la base ---
def init_db(drop_existing: bool = False) -> None:
    """
    Crée toutes les tables dans la base.
    drop_existing : si True, supprime les tables existantes avant création.
    """
    if drop_existing:
        print("[INFO] Dropping existing tables...")
        SQLModel.metadata.drop_all(engine)

    print("[INFO] Creating tables...")
    SQLModel.metadata.create_all(engine)
    print("[INFO] Tables created successfully!")

# --- Attente que PostgreSQL soit prêt ---
def wait_for_postgres(timeout: int = 30, interval: float = 1.0):
    """
    Attend que PostgreSQL soit prêt à accepter les connexions.
    timeout : nombre maximum de secondes avant échec
    interval : temps entre chaque tentative
    """
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

# --- Dependency pour FastAPI ---
def get_db():
    """
    Yield une session SQLModel pour dependency injection dans FastAPI.
    Usage:
        from fastapi import Depends
        def my_route(db: Session = Depends(get_db)):
            ...
    """
    with Session(engine) as session:
        yield session
