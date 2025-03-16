#!/usr/bin/env python3
"""
Gmail API Credentials Setup Script

This script helps users set up their Gmail API credentials for the Email Rules Engine.
It guides users through the process of:
1. Creating a Google Cloud project
2. Enabling the Gmail API
3. Creating OAuth credentials
4. Testing the credentials

Usage:
    python setup_gmail_credentials.py
"""

import os
import sys
import json
import webbrowser
from pathlib import Path

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
except ImportError:
    print("Required packages not found. Installing...")
    os.system(
        "pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
    )
    print("Please restart the script after installation.")
    sys.exit(1)

# Define the scopes
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def print_step(step_number, title):
    """Print a step with formatting."""
    print("\n" + "=" * 80)
    print(f" Step {step_number}: {title} ".center(80, "="))
    print("=" * 80 + "\n")


def check_credentials_file():
    """Check if credentials.json exists."""
    if os.path.exists("credentials.json"):
        with open("credentials.json", "r") as f:
            try:
                creds_data = json.load(f)
                if "installed" in creds_data or "web" in creds_data:
                    return True
            except json.JSONDecodeError:
                pass
    return False


def create_token_file():
    """Create token.json file from credentials.json."""
    print("Authenticating with Google...")

    if not os.path.exists("credentials.json"):
        print("❌ credentials.json not found. Please follow the steps to create it.")
        return False

    try:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

        print("✅ Authentication successful! Token saved to token.json")
        return True
    except Exception as e:
        print(f"❌ Authentication failed: {str(e)}")
        return False


def test_gmail_api():
    """Test the Gmail API with the credentials."""
    print("Testing Gmail API access...")

    if not os.path.exists("token.json"):
        print("❌ token.json not found. Please authenticate first.")
        return False

    try:
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        # If credentials are expired, refresh them
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        # Build the Gmail API service
        service = build("gmail", "v1", credentials=creds)

        # Get the user's email address
        profile = service.users().getProfile(userId="me").execute()
        email = profile.get("emailAddress", "unknown")

        # List a few messages
        results = service.users().messages().list(userId="me", maxResults=5).execute()
        messages = results.get("messages", [])

        if not messages:
            print("✅ API connection successful, but no messages found.")
            return True

        print(
            f"✅ API connection successful! Found {len(messages)} messages for {email}"
        )

        # Get details of the first message
        msg = (
            service.users().messages().get(userId="me", id=messages[0]["id"]).execute()
        )
        headers = {
            header["name"]: header["value"] for header in msg["payload"]["headers"]
        }

        print("\nSample message:")
        print(f"From: {headers.get('From', 'Unknown')}")
        print(f"Subject: {headers.get('Subject', 'No subject')}")
        print(f"Date: {headers.get('Date', 'Unknown')}")

        return True
    except Exception as e:
        print(f"❌ API test failed: {str(e)}")
        return False


def update_env_file():
    """Update .env file with Gmail API settings."""
    env_file = ".env"
    env_example = ".env.example"

    # Check if .env exists, if not, try to copy from .env.example
    if not os.path.exists(env_file):
        if os.path.exists(env_example):
            with open(env_example, "r") as example, open(env_file, "w") as env:
                env.write(example.read())
            print("Created .env file from .env.example")
        else:
            with open(env_file, "w") as env:
                env.write("# Gmail API settings\n")
            print("Created new .env file")

    # Read current .env file
    with open(env_file, "r") as f:
        env_lines = f.readlines()

    # Check if Gmail settings already exist
    gmail_settings = {
        "GMAIL_USER_EMAIL": None,
        "GMAIL_TOKEN_PATH": "token.json",
        "GMAIL_CREDENTIALS_PATH": "credentials.json",
    }

    for i, line in enumerate(env_lines):
        for key in gmail_settings:
            if line.startswith(f"{key}="):
                env_lines[i] = (
                    f"{key}={gmail_settings[key]}\n" if gmail_settings[key] else line
                )
                gmail_settings[key] = None  # Mark as processed

    # Add missing settings
    for key, value in gmail_settings.items():
        if value is not None:
            env_lines.append(f"{key}={value}\n")

    # Write updated .env file
    with open(env_file, "w") as f:
        f.writelines(env_lines)

    print("✅ Updated .env file with Gmail API settings")


def main():
    """Run the Gmail API setup process."""
    print("\n" + "=" * 80)
    print(" GMAIL API CREDENTIALS SETUP ".center(80, "="))
    print("=" * 80 + "\n")

    print(
        "This script will help you set up Gmail API credentials for the Email Rules Engine."
    )

    # Step 1: Check if credentials already exist
    print_step(1, "Checking for existing credentials")
    if check_credentials_file():
        print("✅ credentials.json file found!")
    else:
        print("❌ credentials.json file not found.")

        # Step 2: Guide user to create credentials
        print_step(2, "Creating Google Cloud project and enabling Gmail API")
        print("Please follow these steps to create your credentials:")
        print("1. Go to the Google Cloud Console: https://console.cloud.google.com/")
        print("2. Create a new project or select an existing one")
        print("3. Enable the Gmail API for your project:")
        print("   - Go to 'APIs & Services' > 'Library'")
        print("   - Search for 'Gmail API' and select it")
        print("   - Click 'Enable'")

        # Open the Google Cloud Console
        input("Press Enter to open the Google Cloud Console in your browser...")
        webbrowser.open("https://console.cloud.google.com/")

        print_step(3, "Creating OAuth credentials")
        print("Now, create OAuth 2.0 credentials:")
        print("1. Go to 'APIs & Services' > 'Credentials'")
        print("2. Click 'Create Credentials' > 'OAuth client ID'")
        print("3. Select 'Desktop app' as the application type")
        print("4. Name your client (e.g., 'Email Rules Engine')")
        print("5. Click 'Create'")
        print("6. Download the credentials JSON file")
        print("7. Rename the downloaded file to 'credentials.json'")
        print("8. Move the file to the root directory of this project")

        # Open the Credentials page
        input("Press Enter to open the Credentials page in your browser...")
        webbrowser.open("https://console.cloud.google.com/apis/credentials")

        input("Press Enter once you've downloaded and renamed the credentials file...")

        if not check_credentials_file():
            print(
                "❌ credentials.json still not found. Please make sure you've placed it in the correct location."
            )
            return

        print("✅ credentials.json file found!")

    # Step 4: Create token.json
    print_step(4, "Authenticating with Google")
    if os.path.exists("token.json"):
        print("✅ token.json file already exists.")
        replace = input(
            "Do you want to re-authenticate and replace it? (y/n): "
        ).lower()
        if replace == "y":
            os.remove("token.json")
            if not create_token_file():
                return
    else:
        if not create_token_file():
            return

    # Step 5: Test the API
    print_step(5, "Testing Gmail API access")
    if not test_gmail_api():
        return

    # Step 6: Update .env file
    print_step(6, "Updating environment variables")
    update_env_file()

    print("\n" + "=" * 80)
    print(" SETUP COMPLETED SUCCESSFULLY ".center(80, "="))
    print("=" * 80 + "\n")

    print("Your Gmail API credentials have been set up successfully!")
    print("You can now use the Email Rules Engine with your Gmail account.")
    print("\nNext steps:")
    print("1. Make sure your application is running")
    print("2. Try fetching emails using the API:")
    print('   curl -X GET "http://localhost:8000/api/gmail/messages?max_results=10"')
    print("3. Or run the comprehensive test script:")
    print("   python test_all.py")


if __name__ == "__main__":
    main()
