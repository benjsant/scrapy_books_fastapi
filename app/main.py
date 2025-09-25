"""
Main entry point for the Audiomancy API backend using FastAPI.

This module configures the FastAPI application instance, including CORS settings to allow
requests from specified origins (e.g. local React development servers). It also registers
the Jamendo-related API routes by including the corresponding router.

Attributes:
    app (FastAPI): The FastAPI application instance.
    allowed_origins (List[str]): List of origins allowed to make cross-origin requests.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routes.user_routes import router as user_router
from app.routes.favorite_routes import router as favorite_router
#from app.core.security import get_api_key
from app.errors.handlers import validation_exception_handler
from fastapi.exceptions import RequestValidationError

docs_url = "/docs" if settings.swagger_on else None
redoc_url = "/redoc" if settings.swagger_on else None

app = FastAPI(
    title="Audiomancy API",
    docs_url=docs_url,
    redoc_url=redoc_url
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# personalized handler
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.include_router(user_router)
app.include_router(favorite_router)
