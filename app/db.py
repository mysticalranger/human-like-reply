import motor.motor_asyncio
import os
from bson import ObjectId

MONGO_DETAILS = os.getenv("MONGO_URI")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.social_reply_db4

# Schema validation for write operations
async def setup_schema_validation():
    await database.command({
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
    }})

# Update your save_reply function with better error handling and debugging
async def save_reply(reply_data):
    """
    Save a reply record to the MongoDB database
    """
    # Create a new dictionary to avoid modifying the original
    db_record = reply_data.copy()
    
    # Ensure timestamp is a datetime object (MongoDB requires this)
    if isinstance(db_record["timestamp"], str):
        from datetime import datetime
        db_record["timestamp"] = datetime.fromisoformat(db_record["timestamp"].replace('Z', '+00:00'))
    
    # Make sure platform is acceptable according to schema
    if db_record["platform"].lower() not in ["twitter", "linkedin", "instagram"]:
        db_record["platform"] = "twitter"  # Default fallback
    
    # Debug print - keep this for now
    print(f"⏳ Attempting to save to database: {db_record}")
    
    # Insert the document
    try:
        # Remove the with_options() call that's causing the error
        result = await database.replies.insert_one(db_record)
        
        print(f"✅ Document saved successfully with ID: {result.inserted_id}")
        return str(result.inserted_id)
    except Exception as e:
        error_msg = f"Database insert failed: {str(e)}"
        print(f"❌ ERROR: {error_msg}")
        # Add more context to the error
        raise Exception(error_msg) from e
