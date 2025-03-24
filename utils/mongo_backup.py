import os
from bson import decode_all
from pymongo import MongoClient

# Define the backup directory and connect to MongoDB
backup_dir = "backup_mongo"  # Folder where the .bson files are stored
mongo_uri = "mongodb://localhost:27017/"  # Change this if your MongoDB is hosted elsewhere

# Connect to MongoDB
client = MongoClient(mongo_uri)

# Create (or get) the database 'examples'
db = client["examples"]

# Loop over each file in the backup directory
for file_name in os.listdir(backup_dir):
    # Process only files ending with .bson
    if file_name.endswith(".bson"):
        # Derive collection name from the file name (e.g., "users.bson" -> "users")
        collection_name = os.path.splitext(file_name)[0]
        collection = db[collection_name]
        file_path = os.path.join(backup_dir, file_name)
        
        print(f"Processing file: {file_path} into collection: {collection_name}")
        
        # Open the file in binary mode and decode BSON data
        with open(file_path, "rb") as f:
            file_data = f.read()
            documents = decode_all(file_data)
        
        # Check if any documents were found before inserting
        if documents:
            result = collection.insert_many(documents)
            print(f"Inserted {len(result.inserted_ids)} documents into collection '{collection_name}'.")
        else:
            print(f"No documents found in {file_name}.")
            
print("All BSON files have been processed.")
