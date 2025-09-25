"""
Favorite API Routes
-------------------

This module defines FastAPI routes for managing user favorites.
It includes endpoints to create, delete, list, and rename favorites,
grouped under the "/favorite" prefix with the "Favorite" tag.
"""

from typing import List
from fastapi import APIRouter, status
from app.models.favorite import (
    Favorite,
    FavoriteResponse,
    FavoriteRenameRequest,
    FavoriteCreateRequest,
)
from app.services.favorite.favorite_service import (
    create_favorite_service,
    delete_favorite_service,
    list_favorites_service,
    rename_favorite_service,
)

router = APIRouter(prefix="/favorite", tags=["Favorite"])


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_favorite(request: FavoriteCreateRequest) -> FavoriteResponse:
    """
    Create a new favorite.

    Args:
        request (FavoriteCreateRequest): The request body containing favorite details.

    Returns:
        FavoriteResponse: Response containing success status, message, and created favorite.
    """

    return await create_favorite_service(request)


@router.delete("/delete/{favorite_id}", status_code=status.HTTP_200_OK)
async def delete_favorite(favorite_id: str, user_id: str) -> FavoriteResponse:
    """
    Delete a favorite by its ID.

    Args:
        favorite_id (str): The ID of the favorite to delete.
        user_id (str): The ID of the user who owns the favorite.

    Returns:
        FavoriteResponse: Response containing success status, message, and possibly an error.
    """
    return await delete_favorite_service(favorite_id, user_id)


@router.get("/list/{user_id}", response_model=List[Favorite])
async def list_favorites(user_id: str):
    """
    List all favorites of a user.

    Args:
        user_id (str): The ID of the user whose favorites are to be listed.

    Returns:
        List[Favorite]: A list of all favorites belonging to the user.
    """
    return await list_favorites_service(user_id)


@router.put("/rename", status_code=status.HTTP_200_OK)
async def rename_favorite(request: FavoriteRenameRequest) -> FavoriteResponse:
    """
    Rename a favorite by its ID.

    Args:
        request (FavoriteRenameRequest): The request body containing favorite ID and new name.

    Returns:
        FavoriteResponse: Response containing success status, message, and possibly an error.
    """
    return await rename_favorite_service(request)
