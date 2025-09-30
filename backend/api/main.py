from fastapi import FastAPI
from api.routes import books
from api.routes import analytics
app = FastAPI(title="Books API")

# Routes
app.include_router(books.router)
app.include_router(analytics.router)
