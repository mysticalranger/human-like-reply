from unittest.mock import MagicMock
import pytest
from bson import ObjectId

@pytest.fixture(autouse=True)
def mock_db(monkeypatch):
    """Mock MongoDB operations on the real `app.db.database.replies`."""
    stored = {}

    class MockCollection:
        async def insert_one(self, doc):
            # emulate storing with a real ObjectId
            _id = ObjectId()
            d = doc.copy()
            d["_id"] = _id
            stored[_id] = d
            m = MagicMock()
            m.inserted_id = _id
            return m

        async def find_one(self, query):
            _id = query.get("_id")
            if isinstance(_id, str):
                try:
                    _id = ObjectId(_id)
                except:
                    return None
            return stored.get(_id)

        async def delete_one(self, query):
            _id = query.get("_id")
            if isinstance(_id, str):
                try:
                    _id = ObjectId(_id)
                except:
                    return MagicMock()
            stored.pop(_id, None)
            return MagicMock()

    # Patch only the .replies collection on the existing database object
    import app.db
    monkeypatch.setattr(app.db.database, "replies", MockCollection(), raising=True)

@pytest.fixture
def mock_mistral_client(monkeypatch):
    """Mock Mistral client.chat.complete to avoid real API calls."""
    from app.ai import client

    # This should NOT be an async function
    def fake_complete(*, model, messages, **kwargs):
        # Check if this is an analysis request by looking at the system prompt
        is_analysis = False
        for message in messages:
            if message.get("role") == "system" and "Analyze this social media post" in message.get("content", ""):
                is_analysis = True
                break
                
        # Create the response with appropriate content based on request type
        resp = MagicMock()
        msg = MagicMock()
        
        if is_analysis:
            # For analysis requests, include the expected tone
            msg.content = "Tone: excited, Intent: sharing, Topics: product launch"
        else:
            # For regular reply requests
            msg.content = "Mock reply for social media"
            
        choice = MagicMock()
        choice.message = msg
        resp.choices = [choice]
        return resp

    monkeypatch.setattr(client.chat, "complete", fake_complete)
    return True  # fixture value unused
