import pytest
from fastapi import HTTPException

from app.core.security import get_api_key, swagger_enabled
from app.core import config


def test_get_api_key_valid(monkeypatch):
    """Should return API key if valid."""
    monkeypatch.setattr(config.settings, "api_key", "valid123")
    result = get_api_key("valid123")
    assert result == "valid123"


def test_get_api_key_invalid(monkeypatch):
    """Should raise HTTPException if API key is invalid."""
    monkeypatch.setattr(config.settings, "api_key", "valid123")
    with pytest.raises(HTTPException) as exc:
        get_api_key("wrongkey")
    assert exc.value.status_code == 403
    assert exc.value.detail == "Invalid API Key"


def test_swagger_enabled_true(monkeypatch):
    """Should return True if swagger_on is enabled."""
    monkeypatch.setattr(config.settings, "swagger_on", True)
    assert swagger_enabled() is True


def test_swagger_enabled_false(monkeypatch):
    """Should return False if swagger_on is disabled."""
    monkeypatch.setattr(config.settings, "swagger_on", False)
    assert swagger_enabled() is False
