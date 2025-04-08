import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.collection import Collection
from pymongo.database import Database
from .app_config import settings

logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None
    db: Database = None
    
    @classmethod
    async def connect_to_mongo(cls):
        """Connect to MongoDB database"""
        try:
            cls.client = AsyncIOMotorClient(settings.MONGO_URI, 
                                           serverSelectionTimeoutMS=5000)
            # Verify connection is successful
            await cls.client.server_info()
            cls.db = cls.client[settings.DB_NAME]
            logger.info(f"Connected to MongoDB at {settings.MONGO_URI}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
    
    @classmethod
    async def close_mongo_connection(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            logger.info("Closed MongoDB connection")
    
    @classmethod
    def get_collection(cls, collection_name: str) -> Collection:
        """Get a specific collection from the database"""
        if cls.db is None:
            raise ConnectionError("Database connection not established")
        return cls.db[collection_name] 