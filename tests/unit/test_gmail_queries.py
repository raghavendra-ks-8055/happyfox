import pytest
from unittest.mock import patch, MagicMock

from app.services.gmail_service import GmailService


@pytest.mark.parametrize(
    "query,expected_call",
    [
        ("in:inbox", "in:inbox"),
        ("from:example.com", "from:example.com"),
        ("subject:test", "subject:test"),
        ("is:unread", "is:unread"),
    ],
)
def test_query_parameter(query, expected_call):
    """Test that different query parameters are correctly passed to the Gmail API."""
    with patch("app.services.gmail_service.build") as mock_build, patch(
        "app.services.gmail_service.GmailService.get_credentials"
    ):

        # Setup mock
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_list = mock_service.users().messages().list
        mock_list().execute.return_value = {"messages": []}

        # Call the method with the query
        GmailService.list_messages(query=query)

        # Assert the query was passed correctly
        mock_list.assert_called_once_with(userId="me", q=expected_call, maxResults=10)
