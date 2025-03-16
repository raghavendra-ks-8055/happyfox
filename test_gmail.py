#!/usr/bin/env python3
"""
Simple script to test Gmail API access.
Run this script directly to fetch emails from your Gmail inbox.
"""

import json
from app.services.gmail_service import GmailService


def main():
    print("Fetching emails from raghavendraks.work@gmail.com...")

    # Fetch messages from Gmail
    messages = GmailService.list_messages(max_results=5)

    # Print the results
    print(f"Found {len(messages)} messages:")
    for i, message in enumerate(messages, 1):
        print(f"\nMessage {i}:")
        print(f"From: {message['from']}")
        print(f"Subject: {message['subject']}")
        print(f"Date: {message['date']}")
        print(f"Snippet: {message['snippet']}")

    print("\nTest completed successfully!")


if __name__ == "__main__":
    main()
