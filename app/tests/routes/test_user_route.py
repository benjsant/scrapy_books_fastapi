"""
Integration tests for the User API routes.

Tests POST /user/create, POST /user/login and PUT /user/update endpoints
with mocked services to ensure responses are correct without hitting the database.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app  # ton FastAPI instance
from app.models.user import UserCreateRequest, UserLoginRequest, UserUpdateRequest, UserResponse
from app.core.config import settings

# Headers with valid API key for all requests
HEADERS = {"X-API-KEY": settings.api_key}

client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_user_services(monkeypatch):
    """Mock the user services to avoid real DB calls."""

    async def fake_create_user(request):
        return UserResponse(success=True, message="User created", user=None)

    async def fake_login_user(request):
        return UserResponse(success=True, message="Login successful", user=None)

    async def fake_update_user(request):
        return UserResponse(success=True, message="User updated", user=None)

    # Patch services
    monkeypatch.setattr("app.routes.user_routes.create_user_service", fake_create_user)
    monkeypatch.setattr("app.routes.user_routes.login_user_service", fake_login_user)
    monkeypatch.setattr("app.routes.user_routes.update_user_service", fake_update_user)


def test_create_user():
    payload = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123"
    }
    response = client.post("/user/create", json=payload, headers=HEADERS)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "User created"


def test_login_user():
    payload = {
        "email": "test@example.com",
        "password": "password123"
    }
    response = client.post("/user/login", json=payload, headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Login successful"


def test_update_user():
    payload = {
        "id": "123456",
        "username": "updateduser",
        "password": "newpassword"
    }
    response = client.put("/user/modify", json=payload, headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "User updated"
