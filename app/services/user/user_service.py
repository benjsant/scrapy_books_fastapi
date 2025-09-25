from datetime import datetime, timezone
from typing import Dict, Any

from bson import ObjectId
from fastapi import HTTPException
from passlib.context import CryptContext

from app.core.db import users_collection, check_connection
from app.models.user import (
    UserCreateRequest,
    UserLoginRequest,
    UserUpdateRequest,
    UserCreate,
    User,
    UserResponse,
)

# Context for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def mongo_to_user_doc(document: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a MongoDB document into a dictionary compatible with the User model.

    Args:
        document (dict): The MongoDB document.

    Returns:
        dict: A dictionary with "_id" converted to string as "id".
    """
    return {**document, "id": str(document["_id"])} if "_id" in document else document


def hash_password(password: str) -> str:
    """
    Hash a plain-text password.

    Args:
        password (str): Plain-text password.

    Returns:
        str: Hashed password.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify that a plain-text password matches a hashed password.

    Args:
        plain_password (str): Input password.
        hashed_password (str): Hashed password from DB.

    Returns:
        bool: True if passwords match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


async def create_user_service(request: UserCreateRequest) -> UserResponse:
    """
    Create a new user in MongoDB.

    Args:
        request (UserCreateRequest): The user creation request.

    Raises:
        HTTPException: If the email is already registered.

    Returns:
        UserResponse: Response with user data.
    """
    if not await check_connection():
        raise HTTPException(status_code=503, detail="impossible de se connecter au serveur")
    
    existing = await users_collection.find_one({"email": request.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email déjà enregistré")

    user = UserCreate(
        email=request.email,
        username=request.username,
        password_hash=hash_password(request.password),
        created_at=datetime.now(timezone.utc),
    )

    result = await users_collection.insert_one(user.model_dump())
    doc = mongo_to_user_doc({**user.model_dump(), "_id": result.inserted_id})

    return UserResponse(
        success=True,
        message="User successfully created",
        user=User(**doc).model_dump(by_alias=True),
    )


async def login_user_service(request: UserLoginRequest) -> UserResponse:
    """
    Authenticate a user with email and password.

    Args:
        request (UserLoginRequest): The login request.

    Raises:
        HTTPException: If user is not found or password is incorrect.

    Returns:
        UserResponse: Response with authenticated user data.
    """
    if not await check_connection():
        raise HTTPException(status_code=503, detail="impossible de se connecter au serveur")
    
    existing = await users_collection.find_one({"email": request.email})
    if not existing:
        raise HTTPException(status_code=400, detail="email inconnu")

    if not verify_password(request.password, existing["password_hash"]):
        raise HTTPException(status_code=400, detail="mot de passe invalide")

    doc = mongo_to_user_doc(existing)

    return UserResponse(
        success=True,
        message="Login successful",
        user=User(**doc),
    )


async def update_user_service(request: UserUpdateRequest) -> UserResponse:
    """
    Update an existing user's information in MongoDB.

    Args:
        request (UserUpdateRequest): The update request containing fields to update.

    Raises:
        HTTPException: If user is not found or no valid fields are provided.

    Returns:
        UserResponse: Response with updated user data.
    """
    if not await check_connection():
        raise HTTPException(status_code=503, detail="impossible de se connecter au serveur")
    
    existing = await users_collection.find_one({"_id": ObjectId(request.id)})
    if not existing:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    update_data = {}
    for key, value in request.model_dump().items():
        if value is not None and key != "id":
            if key == "password":
                update_data["password_hash"] = hash_password(value)
            else:
                update_data[key] = value

    if not update_data:
        raise HTTPException(status_code=400, detail="Aucun champ valide à mettre à jour")

    result = await users_collection.update_one(
        {"_id": ObjectId(request.id)}, {"$set": update_data}
    )

    if result.modified_count == 0:
        return UserResponse(
            success=False,
            message="Aucune modification appliquée",
            user=None,
        )

    updated_user = await users_collection.find_one({"_id": ObjectId(request.id)})
    doc = mongo_to_user_doc(updated_user)

    return UserResponse(
        success=True,
        message="L'utilisateur a été mis à jour avec succès",
        user=User(**doc),
    )
