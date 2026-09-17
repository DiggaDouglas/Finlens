import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB_NAME", "finlens_db")

class DatabaseClient:
    _client = None

    @classmethod
    def get_client(cls) -> MongoClient:
        if cls._client is None:
            cls._client = MongoClient(
                MONGO_URI,
                maxPoolSize=50,
                minPoolSize=10,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=10000
            )
        return cls._client

    @classmethod
    def check_connection(cls) -> bool:
        try:
            client = cls.get_client()
            client.admin.command('ping')
            return True
        except ConnectionFailure:
            return False

    @classmethod
    def get_database(cls):
        return cls.get_client()[DB_NAME]