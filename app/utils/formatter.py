"""
Utility functions for normalizing and formatting raw Jamendo track data.

Includes functions to clean up license URLs and convert Jamendo's native data
structure into the response model expected by the API.

Functions:
    normalize_license_url: Cleans license URL by removing region-specific suffixes.
    format_jamendo_track: Formats a single raw track into a JamendoTrackResponse.
"""
from typing import Dict, Any
from typing import List
from urllib.parse import urlparse, urlunparse


def normalize_license_url(url: str) -> str:
    """
    Converts a Jamendo license URL to a normalized base form by:
    - enforcing HTTPS
    - removing region-specific suffixes (e.g., /be/, /fr/)

    This form is used to match against LICENSE_MAP keys.
    """

    if not url:
        return ""
    parsed = urlparse(url)
    path_parts = parsed.path.rstrip("/").split("/")

    # Remove regional suffix if present (e.g., '/be', '/fr')
    if len(path_parts) >= 5 and len(path_parts[-1]) == 2:
        path_parts = path_parts[:-1]

    normalized_path = "/".join(path_parts) + "/"
    return f"https://{parsed.netloc}{normalized_path}"  # Force HTTPS




def mongo_to_user_doc(document: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a MongoDB document into a dictionary compatible with the User model.

    Args:
        document (dict): The MongoDB document.

    Returns:
        dict: A dictionary with "_id" converted to string as "id".
    """
    return {**document, "id": str(document["_id"])} if "_id" in document else document
