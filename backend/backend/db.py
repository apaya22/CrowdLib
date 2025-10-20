from django.conf import settings
import pymongo

class MongoDBConnection:
    """
    Class members manage the connection to MongoDB Atlas
    """
    _client = None
    _db = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._client = pymongo.MongoClient(settings.MONGODB_URI)
        return cls._client

    @classmethod
    def get_db(cls):
        if cls._db is None:
            cls._db = cls.get_client()[settings.MONGODB_NAME]
        return cls._db

    @classmethod
    def close(cls):
        if cls._client:
            cls._client.close()
            cls._client = None
            cls._db = None

def get_collection(collection_name):
    """Helper function to get a collection"""
    db = MongoDBConnection.get_db()
    return db[collection_name]