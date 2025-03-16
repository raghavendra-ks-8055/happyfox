import unittest
from unittest.mock import patch, MagicMock

from app.services.gmail_service import GmailService


class TestGmailService(unittest.TestCase):
    @patch("app.services.gmail_service.build")
    @patch("app.services.gmail_service.Credentials")
    def test_list_messages_basic(self, mock_credentials, mock_build):
        # Set up mocks
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock list response
        mock_service.users().messages().list().execute.return_value = {
            "messages": [{"id": "123", "threadId": "thread123"}]
        }

        # Mock get response
        mock_service.users().messages().get().execute.return_value = {
            "id": "123",
            "threadId": "thread123",
            "labelIds": ["INBOX"],
            "snippet": "Test email",
            "payload": {
                "headers": [
                    {"name": "From", "value": "test@example.com"},
                    {"name": "Subject", "value": "Test Subject"},
                ],
                "body": {"data": "VGVzdCBib2R5"},  # "Test body" in base64
            },
        }

        # Call the method
        messages = GmailService.list_messages(max_results=1)

        # Assertions
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["from"], "test@example.com")
        self.assertEqual(messages[0]["subject"], "Test Subject")


if __name__ == "__main__":
    unittest.main()
