import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app

client = TestClient(app)

# We need to patch all async functions that get called during testing
@pytest.fixture(autouse=True)
def mock_api_dependencies():
    """Mock API dependencies for testing"""
    # Define mocks
    async def mock_generate_reply(platform, post_text):
        return f"This is a mocked reply for {platform}"
    
    async def mock_save_reply(data):
        return "mock_id"

    # Apply patches
    with patch("app.main.generate_reply", mock_generate_reply):
        with patch("app.main.save_reply", mock_save_reply):
            yield

def test_reply_endpoint():
    """Test the /reply endpoint with mocked dependencies"""
    response = client.post(
        "/reply",
        json={"platform": "twitter", "post_text": "Just adopted a new puppy!"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["platform"] == "twitter"
    assert data["post_text"] == "Just adopted a new puppy!"
    assert "mocked reply for twitter" in data["generated_reply"].lower()
    assert data["timestamp"]

def test_platform_normalization():
    """Test that platform names are normalized"""
    response = client.post(
        "/reply",
        json={"platform": "insta", "post_text": "Beach day with friends!"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "mocked reply for instagram" in data["generated_reply"].lower()

def test_error_handling():
    """Test error handling with invalid input"""
    response = client.post(
        "/reply",
        json={}
    )
    
    # Should return a validation error
    assert response.status_code == 422