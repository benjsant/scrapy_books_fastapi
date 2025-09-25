"""
User routes for FastAPI application.

Contains endpoints for creating, logging in, and updating users.
"""

from fastapi import APIRouter, status

from app.models.user import (
    UserCreateRequest,
    UserLoginRequest,
    UserUpdateRequest,
    UserResponse,
)
from app.services.user.user_service import (
    create_user_service,
    login_user_service,
    update_user_service,
)

router = APIRouter(prefix="/user", tags=["Users"])


@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_user(request: UserCreateRequest) -> UserResponse:
    """
    Create a new user.

    Args:
        request (UserCreateRequest): The request body containing user details.

    Returns:
        UserResponse: Response containing success status, message, and created user.
    """
    return await create_user_service(request)


@router.post("/login", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def login_user(request: UserLoginRequest) -> UserResponse:
    """
    Authenticate a user with email and password.

    Args:
        request (UserLoginRequest): The login credentials.

    Returns:
        UserResponse: Response containing success status, message, and user data.
    """
    return await login_user_service(request)


@router.put("/modify", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def update_user(request: UserUpdateRequest) -> UserResponse:
    """
    Update an existing user's information.

    Args:
        request (UserUpdateRequest): The request body containing updated fields.

    Returns:
        UserResponse: Response containing success status, message, and updated user.
    """
    return await update_user_service(request)
