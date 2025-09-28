from fastapi import FastAPI
from api.routes import books

app = FastAPI(title="Books API")

# Routes
app.include_router(books.router)
