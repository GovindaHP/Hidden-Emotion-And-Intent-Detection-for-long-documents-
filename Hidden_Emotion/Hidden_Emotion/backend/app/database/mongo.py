import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from app.database.db_fallback import local_db

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.db = None
        self.is_mongo_connected = False

    async def connect(self):
        try:
            self.client = AsyncIOMotorClient(
                settings.MONGODB_URL, 
                serverSelectionTimeoutMS=2000
            )
            # Ping database
            await self.client.admin.command('ping')
            self.db = self.client[settings.DATABASE_NAME]
            self.is_mongo_connected = True
            logger.info("Successfully connected to MongoDB.")
        except Exception as e:
            logger.warning(f"MongoDB connection failed ({e}). Falling back to high-performance local JSON DB storage.")
            self.is_mongo_connected = False

    async def disconnect(self):
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed.")

    async def insert_one(self, collection_name: str, document: dict):
        if self.is_mongo_connected:
            res = await self.db[collection_name].insert_one(document)
            document["_id"] = str(res.inserted_id)
            return document
        return local_db.insert_one(collection_name, document)

    async def find_one(self, collection_name: str, query: dict):
        if self.is_mongo_connected:
            res = await self.db[collection_name].find_one(query)
            if res and "_id" in res:
                res["_id"] = str(res["_id"])
            return res
        return local_db.find_one(collection_name, query)

    async def find(self, collection_name: str, query: dict = None, limit: int = 100):
        if query is None:
            query = {}
        if self.is_mongo_connected:
            cursor = self.db[collection_name].find(query).limit(limit)
            docs = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                docs.append(doc)
            return docs
        return local_db.find(collection_name, query, limit=limit)

    async def update_one(self, collection_name: str, query: dict, update: dict):
        if self.is_mongo_connected:
            res = await self.db[collection_name].update_one(query, update)
            return res.modified_count > 0
        return local_db.update_one(collection_name, query, update)

    async def delete_one(self, collection_name: str, query: dict):
        if self.is_mongo_connected:
            res = await self.db[collection_name].delete_one(query)
            return res.deleted_count > 0
        return local_db.delete_one(collection_name, query)

    async def count(self, collection_name: str, query: dict = None):
        if query is None:
            query = {}
        if self.is_mongo_connected:
            return await self.db[collection_name].count_documents(query)
        return local_db.count(collection_name, query)

db_manager = DatabaseManager()
