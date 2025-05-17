import motor.motor_asyncio
import asyncio
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

async def test_connection():
    # Get MongoDB URI
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        print("❌ ERROR: MONGO_URI environment variable is not set!")
        print("Please create a .env file with your MONGO_URI")
        return False
    
    print(f"Connecting to: {mongo_uri}")
    
    try:
        # Create client
        client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)
        
        # Connect to database
        db = client.social_reply_db1
        
        # Test insert operation with a valid platform value
        test_doc = {
            "platform": "twitter", # Changed from "test" to a valid value
            "post_text": "Test connection",
            "generated_reply": "Test successful",
            "timestamp": datetime.now()
        }
        
        result = await db.replies.insert_one(test_doc)
        print(f"✅ Successfully inserted document with ID: {result.inserted_id}")
        
        # Clean up
        await db.replies.delete_one({"_id": result.inserted_id})
        print("✅ Test document removed")
        return True
    
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    if success:
        print("✅ MongoDB connection successful!")
    else:
        print("❌ MongoDB connection failed!")