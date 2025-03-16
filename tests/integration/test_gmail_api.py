import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime

from app.main import app
from app.services.gmail_service import GmailService


client = TestClient(app)


@pytest.fixture
def mock_gmail_messages():
    """Mock Gmail messages for testing."""
    return [
        {
            "id": "msg_1",
            "threadId": "thread_1",
            "labelIds": ["INBOX", "UNREAD"],
            "snippet": "This is a test email",
            "from": "sender@example.com",
            "to": "recipient@example.com",
            "subject": "Test Email 1",
            "date": "Mon, 15 Nov 2023 14:30:00 +0000",
            "received_date": datetime.now(),
            "message": "This is the body of test email 1",
        },
        {
            "id": "msg_2",
            "threadId": "thread_2",
            "labelIds": ["INBOX"],
            "snippet": "Another test email",
            "from": "another@example.com",
            "to": "recipient@example.com",
            "subject": "Test Email 2",
            "date": "Tue, 16 Nov 2023 10:15:00 +0000",
            "received_date": datetime.now(),
            "message": "This is the body of test email 2",
        },
    ]


@patch.object(GmailService, "list_messages")
def test_get_gmail_messages(mock_list_messages, mock_gmail_messages):
    """Test the GET /api/gmail/messages endpoint."""
    # Mock the GmailService.list_messages method
    mock_list_messages.return_value = mock_gmail_messages

    # Make the request
    response = client.get("/api/gmail/messages?max_results=2")

    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == "msg_1"
    assert data[1]["id"] == "msg_2"
    assert "actions" in data[0]
    assert "actions" in data[1]


@patch.object(GmailService, "list_messages")
def test_sync_gmail_messages(mock_list_messages, mock_gmail_messages):
    """Test the POST /api/gmail/sync endpoint."""
    # Mock the GmailService.list_messages method
    mock_list_messages.return_value = mock_gmail_messages

    # Make the request
    response = client.post("/api/gmail/sync?max_results=2")

    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert "gmail_id" in data[0]
    assert "gmail_id" in data[1]
    assert data[0]["gmail_id"] == "msg_1"
    assert data[1]["gmail_id"] == "msg_2"


def test_get_emails():
    """Test the GET /api/emails endpoint."""
    # Make the request
    response = client.get("/api/emails")

    # Check the response
    assert response.status_code == 200
    assert isinstance(response.json(), list)
