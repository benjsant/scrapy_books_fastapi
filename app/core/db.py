"""
Database module for MongoDB connection and collections using Motor.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError
from app.core.config import settings

MONGO_HOST = settings.mongo_host
MONGO_PORT = settings.mongo_port
MONGO_USERNAME = settings.mongo_username
MONGO_PASSWORD = settings.mongo_password
MONGO_DBNAME = settings.mongo_db_name

if MONGO_USERNAME and MONGO_PASSWORD:
    MONGO_URL = (
        f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}"
        f"@{MONGO_HOST}:{MONGO_PORT}/"
        "?ssl=true&replicaSet=globaldb&retrywrites=false"
    )
else:
    MONGO_URL = f"mongodb://{MONGO_HOST}:{MONGO_PORT}"

# Initialize client and database
client = AsyncIOMotorClient(MONGO_URL)
db = client[MONGO_DBNAME]

# Collections
users_collection = db["user"]
favorite_collection = db["favorite"]

async def check_connection() -> bool:
    """
    Check if the MongoDB connection is alive.

    Returns:
        bool: True if connection is successful, False otherwise.
    """
    try:
        await client.admin.command("ping")
        return True
    except PyMongoError:
        return False
