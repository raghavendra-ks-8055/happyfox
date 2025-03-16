import os
import json
import base64
import re
import requests
from typing import List, Dict, Any
from datetime import datetime
from bs4 import BeautifulSoup

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Define the scopes
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


class GmailService:
    """Simple service for interacting with Gmail API."""

    @staticmethod
    def get_credentials(
        token_path: str = "token.json", credentials_path: str = "credentials.json"
    ) -> Credentials:
        """
        Get or refresh credentials for Gmail API.

        Args:
            token_path: Path to the token file
            credentials_path: Path to the credentials file

        Returns:
            Credentials: The OAuth credentials
        """
        creds = None

        # Check if token.json exists
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_info(
                json.loads(open(token_path).read()), SCOPES
            )

        # If there are no valid credentials, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(token_path, "w") as token:
                token.write(creds.to_json())

        return creds

    @staticmethod
    def list_messages(
        max_results: int = 10, query: str = "in:inbox"
    ) -> List[Dict[str, Any]]:
        """
        List messages from Gmail inbox.

        Args:
            max_results: Maximum number of messages to return
            query: Gmail search query

        Returns:
            List[Dict[str, Any]]: List of messages
        """
        try:
            # Get credentials and build service
            creds = GmailService.get_credentials()
            service = build("gmail", "v1", credentials=creds)

            # Get message IDs
            results = (
                service.users()
                .messages()
                .list(userId="me", q=query, maxResults=max_results)
                .execute()
            )

            messages = results.get("messages", [])

            if not messages:
                return []

            # Get full message details
            detailed_messages = []
            for message in messages:
                msg = (
                    service.users()
                    .messages()
                    .get(userId="me", id=message["id"], format="full")
                    .execute()
                )

                # Extract headers
                headers = {}
                for header in msg["payload"]["headers"]:
                    headers[header["name"].lower()] = header["value"]

                # Extract body
                body = ""
                if "parts" in msg["payload"]:
                    for part in msg["payload"]["parts"]:
                        if part["mimeType"] == "text/plain":
                            if "data" in part["body"]:
                                body = base64.urlsafe_b64decode(
                                    part["body"]["data"]
                                ).decode("utf-8")
                                break
                elif "body" in msg["payload"] and "data" in msg["payload"]["body"]:
                    body = base64.urlsafe_b64decode(
                        msg["payload"]["body"]["data"]
                    ).decode("utf-8")

                # Format the message
                formatted_message = {
                    "id": msg["id"],
                    "thread_id": msg["threadId"],
                    "label_ids": msg["labelIds"],
                    "snippet": msg["snippet"],
                    "from": headers.get("from", ""),
                    "to": headers.get("to", ""),
                    "subject": headers.get("subject", ""),
                    "date": headers.get("date", ""),
                    "received_date": datetime.now(),  # Use current time as fallback
                    "message": body,
                }

                # Try to parse the date
                if "date" in headers:
                    try:
                        from email.utils import parsedate_to_datetime

                        formatted_message["received_date"] = parsedate_to_datetime(
                            headers["date"]
                        )
                    except:
                        pass

                detailed_messages.append(formatted_message)

            return detailed_messages

        except HttpError as error:
            print(f"An error occurred: {error}")
            return []

    @staticmethod
    def fetch_emails(
        max_results: int = 10,
        query: str = "in:inbox",
    ) -> List[Dict[str, Any]]:
        """
        Fetch emails using the Gmail API.

        Args:
            max_results: Maximum number of messages to return
            query: Gmail search query

        Returns:
            List[Dict[str, Any]]: List of messages
        """
        return GmailService.list_messages(max_results=max_results, query=query)
