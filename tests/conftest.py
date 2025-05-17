import pytest
import os
import sys
from dotenv import load_dotenv

# Ensure the app module can be imported regardless of where tests are run from
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Load environment variables for tests
load_dotenv()

# Import our mocks so they're available to all tests
from tests.mocks import mock_mistral_client, mock_db

@pytest.fixture
def sample_posts():
    """Provides sample posts for different platforms to use in tests"""
    return {
        "linkedin": "Excited to announce I've joined Google as a Senior Product Manager!",
        "twitter": "Anyone else watching the game tonight? Can't believe that last play! #sports",
        "instagram": "Perfect beach day ☀️ Nothing better than sun, sand, and good friends! #beachvibes"
    }