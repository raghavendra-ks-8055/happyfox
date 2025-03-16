#!/usr/bin/env python3
"""
Gmail OAuth Setup Script

This script helps you set up OAuth credentials for Gmail API access.
It will guide you through the OAuth flow and save the credentials to a token.json file.
"""

import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# Define the scopes
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def main():
    """Run the OAuth flow and save the credentials."""
    creds = None

    # Check if token.json exists
    if os.path.exists("token.json"):
        print("Existing token.json found. Loading credentials...")
        creds = Credentials.from_authorized_user_info(
            json.loads(open("token.json").read()), SCOPES
        )

    # If there are no valid credentials, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            print("Starting OAuth flow...")
            # Check if credentials.json exists
            if not os.path.exists("credentials.json"):
                print("Error: credentials.json not found.")
                print(
                    "Please create a credentials.json file with your OAuth client ID and secret."
                )
                return

            # Create the flow using the client secrets file
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES,
                # Use the exact redirect URI that's configured in Google Cloud Console
                redirect_uri="http://localhost:8000/api/gmail/callback",
            )

            # Instead of using run_local_server, use run_flow with a custom server
            # This is more advanced and requires additional code
            # For simplicity, it's better to update the Google Cloud Console settings

            # Run the local server flow
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
            print("Credentials saved to token.json")

    print("OAuth setup complete. You can now use the Gmail API.")


if __name__ == "__main__":
    main()
