import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from bson import ObjectId
from fastapi import HTTPException

from app.services.user.user_service import (
    create_user_service,
    login_user_service,
    update_user_service,
    hash_password,
    verify_password,
)
from app.models.user import UserCreateRequest, UserLoginRequest, UserUpdateRequest


@pytest.mark.asyncio
async def test_create_user_success():
    request = UserCreateRequest(email="test@example.com", username="testuser", password="password123")

    mock_insert_result = MagicMock()
    mock_insert_result.inserted_id = ObjectId()

    with patch("app.services.user.user_service.check_connection", new_callable=AsyncMock) as mock_check, \
         patch("app.services.user.user_service.users_collection.find_one", new_callable=AsyncMock) as mock_find, \
         patch("app.services.user.user_service.users_collection.insert_one", new_callable=AsyncMock) as mock_insert:

        mock_check.return_value = True
        mock_find.return_value = None
        mock_insert.return_value = mock_insert_result

        response = await create_user_service(request)

    assert response.success is True
    assert response.user.email == "test@example.com"
    mock_check.assert_awaited_once()
    mock_find.assert_awaited_once_with({"email": "test@example.com"})
    mock_insert.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_user_email_exists():
    request = UserCreateRequest(email="test@example.com", username="testuser", password="password123")

    with patch("app.services.user.user_service.check_connection", new_callable=AsyncMock) as mock_check, \
         patch("app.services.user.user_service.users_collection.find_one", new_callable=AsyncMock) as mock_find:

        mock_check.return_value = True
        mock_find.return_value = {"email": "test@example.com"}

        with pytest.raises(HTTPException) as exc:
            await create_user_service(request)

        assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_login_user_success():
    request = UserLoginRequest(email="test@example.com", password="password123")
    hashed_password = hash_password("password123")

    user_doc = {"_id": ObjectId(), "email": "test@example.com", "username": "testuser", "password_hash": hashed_password}

    with patch("app.services.user.user_service.check_connection", new_callable=AsyncMock) as mock_check, \
         patch("app.services.user.user_service.users_collection.find_one", new_callable=AsyncMock) as mock_find:

        mock_check.return_value = True
        mock_find.return_value = user_doc

        response = await login_user_service(request)

    assert response.success is True
    assert response.user.email == "test@example.com"


@pytest.mark.asyncio
async def test_login_user_wrong_password():
    request = UserLoginRequest(email="test@example.com", password="wrongpassword")
    hashed_password = hash_password("password123")

    user_doc = {"_id": ObjectId(), "email": "test@example.com", "username": "testuser", "password_hash": hashed_password}

    with patch("app.services.user.user_service.check_connection", new_callable=AsyncMock) as mock_check, \
         patch("app.services.user.user_service.users_collection.find_one", new_callable=AsyncMock) as mock_find:

        mock_check.return_value = True
        mock_find.return_value = user_doc

        with pytest.raises(HTTPException) as exc:
            await login_user_service(request)
        assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_update_user_success():
    request = UserUpdateRequest(id=str(ObjectId()), username="newname", password="newpass")
    user_id = ObjectId(request.id)
    existing_user = {"_id": user_id, "email": "test@example.com", "username": "oldname", "password_hash": hash_password("oldpass")}

    mock_update_result = MagicMock()
    mock_update_result.modified_count = 1

    with patch("app.services.user.user_service.check_connection", new_callable=AsyncMock) as mock_check, \
         patch("app.services.user.user_service.users_collection.find_one", new_callable=AsyncMock) as mock_find, \
         patch("app.services.user.user_service.users_collection.update_one", new_callable=AsyncMock) as mock_update:

        mock_check.return_value = True
        mock_find.side_effect = [existing_user, {**existing_user, "username": "newname"}]
        mock_update.return_value = mock_update_result

        response = await update_user_service(request)

    assert response.success is True
    assert response.user.username == "newname"


@pytest.mark.asyncio
async def test_update_user_no_changes():
    request = UserUpdateRequest(id=str(ObjectId()), username=None, password=None)
    user_id = ObjectId(request.id)
    existing_user = {"_id": user_id, "email": "test@example.com", "username": "oldname", "password_hash": hash_password("oldpass")}

    with patch("app.services.user.user_service.check_connection", new_callable=AsyncMock) as mock_check, \
         patch("app.services.user.user_service.users_collection.find_one", new_callable=AsyncMock) as mock_find:

        mock_check.return_value = True
        mock_find.return_value = existing_user

        with pytest.raises(HTTPException) as exc:
            await update_user_service(request)
        assert exc.value.status_code == 400
