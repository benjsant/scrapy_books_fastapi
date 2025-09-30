from sqlmodel import create_engine, SQLModel
from api.core.config import settings

# Utilise le database_url dynamique (Key Vault ou fallback local)
engine = create_engine(settings.database_url, echo=True)


def init_db() -> None:
    """
    Import all models and create all tables in the database.
    Drops existing tables if you want a fresh start.
    """
    from db.models import Book, Category, ProductType, Tax

    # Si tu veux DROP les tables existantes à chaque init :
    SQLModel.metadata.drop_all(engine)

    SQLModel.metadata.create_all(engine)