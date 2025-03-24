# database/mongo_client.py

from pymongo import MongoClient
from config.settings import MONGO_URI, DB_NAME

# Create a global MongoClient instance.
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

def get_collection(collection_name: str):
    """
    Returns a reference to a collection by name.
    E.g. get_collection("TeamA_commits") -> the 'TeamA_commits' collection
    """
    return db[collection_name]
