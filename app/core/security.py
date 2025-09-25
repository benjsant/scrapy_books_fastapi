"""
Security utilities for API key authentication.

Validates that requests contain the correct API key from settings.
"""

from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from app.core.config import settings

# api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=True)

# def get_api_key(api_key: str = Security(api_key_header)):
#     """
#     Vérifie la clé API. Lève une erreur si invalide.
#     """
#     if api_key != settings.api_key:
#         raise HTTPException(status_code=403, detail="Invalid API Key")
#     return api_key

def swagger_enabled() -> bool:
    """
    Retourne True si Swagger doit être activé.
    """
    return settings.swagger_on
