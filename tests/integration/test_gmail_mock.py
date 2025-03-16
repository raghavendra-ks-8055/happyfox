import unittest
from unittest.mock import patch
import json
import base64
from datetime import datetime

from fastapi.testclient import TestClient

from app.main import app


class TestGmailApiEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch("app.services.gmail_service.GmailService.list_messages")
    def test_get_gmail_messages(self, mock_list_messages):
        # Mock the Gmail service response
        mock_list_messages.return_value = [
            {
                "id": "msg1",
                "thread_id": "thread1",
                "label_ids": ["INBOX"],
                "snippet": "This is a test email",
                "from": "sender@example.com",
                "to": "recipient@example.com",
                "subject": "Test Email",
                "date": "Mon, 15 Nov 2023 14:30:00 +0000",
                "received_date": datetime.now(),
                "message": "This is a test email body",
            }
        ]

        # Call the API endpoint
        response = self.client.get("/api/gmail/messages?max_results=1")

        # Assertions
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], "msg1")
        self.assertEqual(data[0]["from"], "sender@example.com")
        self.assertEqual(data[0]["subject"], "Test Email")
        self.assertIn("actions", data[0])


if __name__ == "__main__":
    unittest.main()
