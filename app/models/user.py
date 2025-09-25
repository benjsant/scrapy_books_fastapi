from datetime import datetime
from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field, EmailStr, ConfigDict


class User(BaseModel):
    """
    Represents a user stored in the database.
    """
    id: str
    email: EmailStr
    username: str
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(populate_by_name=True)


class UserCreate(BaseModel):
    """
    Represents a user object ready to be inserted into the database.
    """
    email: EmailStr
    username: str
    password_hash: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserCreateRequest(BaseModel):
    """
    Request model for creating a new user (API input).
    """
    email: EmailStr
    username: str
    password: str


class UserLoginRequest(BaseModel):
    """
    Request model for user login (API input).
    """
    email: EmailStr
    password: str


class UserUpdateRequest(BaseModel):
    """
    Request model for updating an existing user.
    Only fields provided will be updated.
    """
    id: str
    username: Optional[str] = None
    password: Optional[str] = None


class UserResponse(BaseModel):
    """
    Standard response model for user operations.
    """
    success: bool
    message: str
    user: Optional[User]
