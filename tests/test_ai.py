import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import pytest
from app.ai import analyze_post, generate_reply
from unittest.mock import patch, AsyncMock

# Import mock fixture
from tests.mocks import mock_mistral_client

@pytest.mark.asyncio
async def test_analyze_post(mock_mistral_client):
    """Test post analysis with mocked Mistral response"""
    sample_post = "Just launched our new product after 6 months of hard work. So excited to share it with you all!"
    
    analysis = await analyze_post(sample_post)
    
    assert analysis is not None, "Analysis should not be empty"
    assert "Tone: excited" in analysis or "excited" in analysis.lower(), "Should detect excited tone"

@pytest.mark.asyncio
async def test_platform_specific_replies(mock_mistral_client):
    """Test platform-specific replies with mocked responses"""
    test_post = "I just completed my first marathon!"
    
    # Use patch to mock analyze_post to return a fixed value
    with patch('app.ai.analyze_post', new=AsyncMock(return_value="Tone: excited, Intent: sharing, Topics: achievement")):
        linkedin_reply = await generate_reply("linkedin", test_post)
        twitter_reply = await generate_reply("twitter", test_post)
        instagram_reply = await generate_reply("instagram", test_post)
        
        # Basic assertions that replies exist
        assert linkedin_reply, "LinkedIn reply should not be empty"
        assert twitter_reply, "Twitter reply should not be empty"
        assert instagram_reply, "Instagram reply should not be empty"

@pytest.mark.asyncio
async def test_reply_personalization(mock_mistral_client):
    """Test reply personalization with mocked response"""
    post_with_specifics = "I'm learning Python programming and just built my first web app using FastAPI!"
    
    # We just need to verify it doesn't error with our mock
    reply = await generate_reply("twitter", post_with_specifics)
    assert reply, "Reply should not be empty"