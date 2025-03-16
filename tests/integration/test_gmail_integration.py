import os
import pytest
from datetime import datetime

from app.services.gmail_service import GmailService


@pytest.mark.skipif(
    not os.path.exists("credentials.json"), reason="credentials.json not found"
)
def test_list_messages_integration():
    """
    Integration test for listing Gmail messages.

    Note: This test requires valid credentials.json file and internet connection.
    It will attempt to authenticate with Gmail API.
    """
    # Get messages from Gmail
    messages = GmailService.list_messages(max_results=3)

    # Basic assertions
    assert isinstance(messages, list)
    if messages:  # Only test if there are messages
        assert len(messages) <= 3

        # Check message structure
        message = messages[0]
        assert "id" in message
        assert "from" in message
        assert "subject" in message
        assert "message" in message
        assert "received_date" in message
