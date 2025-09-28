from sqlmodel import create_engine, SQLModel
from pathlib import Path

# PostgreSQL connection string
DATABASE_URL = "postgresql://books_user:books_password@localhost:5432/books_db"

# Création de l'engine SQLAlchemy/SQLModel
engine = create_engine(DATABASE_URL, echo=True)
