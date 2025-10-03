"""
Main FastAPI application entry point.
Initializes the API and includes all route modules.
"""

from fastapi import FastAPI
from api.routes import books, analytics, snapshot

app = FastAPI(title="Books API")

# Include API routers
app.include_router(books.router)
app.include_router(analytics.router)
app.include_router(snapshot.router) 