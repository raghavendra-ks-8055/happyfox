import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from app.services.gmail_service import GmailService


@pytest.fixture
def mock_gmail_service():
    """Fixture to create a mock Gmail service."""
    with patch("app.services.gmail_service.build") as mock_build:
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock list response
        mock_service.users().messages().list().execute.return_value = {
            "messages": [
                {"id": "msg1", "threadId": "thread1"},
                {"id": "msg2", "threadId": "thread2"},
            ]
        }

        # Mock get responses for two different messages
        mock_get = mock_service.users().messages().get().execute
        mock_get.side_effect = [
            {
                "id": "msg1",
                "threadId": "thread1",
                "labelIds": ["INBOX"],
                "snippet": "This is a test email",
                "payload": {
                    "headers": [
                        {"name": "From", "value": "sender@example.com"},
                        {"name": "To", "value": "recipient@example.com"},
                        {"name": "Subject", "value": "Test Email"},
                        {"name": "Date", "value": "Mon, 15 Nov 2023 14:30:00 +0000"},
                    ],
                    "parts": [
                        {
                            "mimeType": "text/plain",
                            "body": {
                                "data": "VGhpcyBpcyBhIHRlc3QgZW1haWwgYm9keQ=="  # "This is a test email body" in base64
                            },
                        }
                    ],
                },
            },
            {
                "id": "msg2",
                "threadId": "thread2",
                "labelIds": ["INBOX"],
                "snippet": "Another test email",
                "payload": {
                    "headers": [
                        {"name": "From", "value": "another@example.com"},
                        {"name": "To", "value": "recipient@example.com"},
                        {"name": "Subject", "value": "Another Test"},
                        {"name": "Date", "value": "Tue, 16 Nov 2023 10:15:00 +0000"},
                    ],
                    "body": {
                        "data": "QW5vdGhlciB0ZXN0IGVtYWlsIGJvZHk="  # "Another test email body" in base64
                    },
                },
            },
        ]

        yield mock_service


@pytest.fixture
def mock_credentials():
    """Fixture to mock the credentials."""
    with patch("app.services.gmail_service.Credentials") as mock_creds:
        yield mock_creds


def test_list_messages(mock_gmail_service, mock_credentials):
    """Test that list_messages correctly fetches and formats email messages."""
    # Call the method
    messages = GmailService.list_messages(max_results=2)

    # Assertions
    assert len(messages) == 2
    assert messages[0]["id"] == "msg1"
    assert messages[0]["from"] == "sender@example.com"
    assert messages[0]["subject"] == "Test Email"
    assert messages[0]["message"] == "This is a test email body"

    assert messages[1]["id"] == "msg2"
    assert messages[1]["from"] == "another@example.com"
    assert messages[1]["subject"] == "Another Test"
    assert messages[1]["message"] == "Another test email body"


def test_get_credentials():
    """Test the credential retrieval logic."""
    with patch("app.services.gmail_service.os.path.exists", return_value=True), patch(
        "app.services.gmail_service.open", create=True
    ), patch("app.services.gmail_service.json.loads") as mock_json, patch(
        "app.services.gmail_service.Credentials.from_authorized_user_info"
    ) as mock_from_info:

        # Setup
        mock_json.return_value = {"token": "fake_token"}
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_from_info.return_value = mock_creds

        # Call
        result = GmailService.get_credentials()

        # Assert
        assert result == mock_creds
        mock_from_info.assert_called_once_with(
            {"token": "fake_token"}, ["https://www.googleapis.com/auth/gmail.readonly"]
        )
