import os
import sys
import pytest
from bson import ObjectId
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from app.db import save_reply, database

@pytest.mark.asyncio
async def test_save_reply():
    """Test saving a reply to the database with mocked MongoDB"""
    test_reply = {
        "platform": "twitter",
        "post_text": "Testing database integration",
        "generated_reply": "This is a test reply",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    # Save the reply
    result_id = await save_reply(test_reply)
    # Should return a valid ObjectId string
    assert ObjectId.is_valid(result_id), f"Returned ID {result_id!r} is not a valid ObjectId"

    # Retrieve and verify
    saved_reply = await database.replies.find_one({"_id": ObjectId(result_id)})
    assert saved_reply["generated_reply"] == "This is a test reply"
