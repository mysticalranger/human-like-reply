import os
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client.social_reply_db4

# Create collection if it doesn't exist
if "replies" not in db.list_collection_names():
    db.create_collection("replies")

# Set schema validation
db.command({
    "collMod": "replies",
    "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["platform", "post_text", "generated_reply", "timestamp"],
            "properties": {
                "platform": {
                    "bsonType": "string",
                    "enum": ["twitter", "linkedin", "instagram"],
                    "description": "must be a valid platform"
                },
                "post_text": {
                    "bsonType": "string",
                    "minLength": 1,
                    "description": "must be a non-empty string"
                },
                "generated_reply": {
                    "bsonType": "string",
                    "minLength": 1,
                    "description": "must be a non-empty string"
                },
                "timestamp": {
                    "bsonType": "date",
                    "description": "must be a valid date"
                }
            }
        }
    }
})

print("Database and collection initialized with schema validation.")