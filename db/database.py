from sqlmodel import create_engine, SQLModel

# PostgreSQL connection string
DATABASE_URL = "postgresql://books_user:books_password@localhost:5432/books_db"

# Création de l'engine SQLAlchemy/SQLModel
engine = create_engine(DATABASE_URL, echo=True)


def init_db() -> None:
    """
    Import all models and create all tables in the database.
    Drops existing tables if you want a fresh start.
    """
    from db.models import Book, Category, ProductType, Tax

    # Si tu veux DROP les tables existantes à chaque init :
    SQLModel.metadata.drop_all(engine)

    SQLModel.metadata.create_all(engine)