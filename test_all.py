#!/usr/bin/env python3
"""
Comprehensive test script for the Email Rules Engine.
This script tests all major components of the application:
1. Rule creation and management
2. Email fetching from Gmail
3. Email processing with rules
4. Action execution

Usage:
    python test_all.py
"""

import requests
import json
import time
from datetime import datetime, timedelta
from uuid import UUID

# Base URL for the API
BASE_URL = "http://localhost:8000/api"


class UUIDEncoder(json.JSONEncoder):
    """JSON encoder that handles UUID objects."""

    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


def print_section(title):
    """Print a section title with formatting."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")


def test_rule_management():
    """Test rule creation, retrieval, update, and deletion."""
    print_section("Testing Rule Management")

    # Create a rule
    rule_data = {
        "name": "Test Rule",
        "match_type": "all",
        "conditions": [
            {"field": "from", "predicate": "contains", "value": "test@example.com"},
            {"field": "subject", "predicate": "contains", "value": "Test"},
        ],
        "actions": [
            {"type": "mark_as_read"},
            {"type": "move_message", "target": "Test Folder"},
        ],
    }

    print("Creating a new rule...")
    response = requests.post(f"{BASE_URL}/rules", json=rule_data)

    if response.status_code == 201:
        rule = response.json()
        rule_id = rule["id"]
        print(f"✅ Rule created successfully with ID: {rule_id}")
        print(json.dumps(rule, indent=2, cls=UUIDEncoder))
    else:
        print(f"❌ Failed to create rule: {response.status_code}")
        print(response.text)
        return None

    # Get all rules
    print("\nRetrieving all rules...")
    response = requests.get(f"{BASE_URL}/rules")

    if response.status_code == 200:
        rules = response.json()
        print(f"✅ Retrieved {len(rules)} rules")
    else:
        print(f"❌ Failed to retrieve rules: {response.status_code}")

    # Get the specific rule
    print(f"\nRetrieving rule with ID: {rule_id}...")
    response = requests.get(f"{BASE_URL}/rules/{rule_id}")

    if response.status_code == 200:
        rule = response.json()
        print(f"✅ Retrieved rule: {rule['name']}")
    else:
        print(f"❌ Failed to retrieve rule: {response.status_code}")

    # Update the rule
    update_data = {
        "name": "Updated Test Rule",
        "match_type": "any",
        "conditions": [
            {"field": "from", "predicate": "contains", "value": "updated@example.com"},
            {"field": "subject", "predicate": "contains", "value": "Updated"},
        ],
        "actions": [{"type": "mark_as_unread"}],
    }

    print(f"\nUpdating rule with ID: {rule_id}...")
    response = requests.put(f"{BASE_URL}/rules/{rule_id}", json=update_data)

    if response.status_code == 200:
        updated_rule = response.json()
        print(f"✅ Rule updated successfully: {updated_rule['name']}")
        print(json.dumps(updated_rule, indent=2, cls=UUIDEncoder))
    else:
        print(f"❌ Failed to update rule: {response.status_code}")
        print(response.text)

    # Delete the rule
    print(f"\nDeleting rule with ID: {rule_id}...")
    response = requests.delete(f"{BASE_URL}/rules/{rule_id}")

    if response.status_code == 204:
        print("✅ Rule deleted successfully")
    else:
        print(f"❌ Failed to delete rule: {response.status_code}")
        print(response.text)

    return rule_id


def test_gmail_integration():
    """Test Gmail API integration for fetching emails."""
    print_section("Testing Gmail Integration")

    # Test fetching emails using the API method
    print("Fetching emails using Gmail API...")
    response = requests.get(f"{BASE_URL}/gmail/messages?max_results=5")

    if response.status_code == 200:
        emails = response.json()
        print(f"✅ Successfully fetched {len(emails)} emails using Gmail API")
        if emails:
            print("\nSample email:")
            print(f"From: {emails[0]['from']}")
            print(f"Subject: {emails[0]['subject']}")
            print(f"Snippet: {emails[0]['snippet']}")
    else:
        print(f"❌ Failed to fetch emails using Gmail API: {response.status_code}")
        print(response.text)

    # Test syncing emails to the database
    print("\nSyncing emails to the database...")
    response = requests.post(f"{BASE_URL}/gmail/sync?max_results=5")

    if response.status_code == 200:
        emails = response.json()
        print(f"✅ Successfully synced {len(emails)} emails to the database")
    else:
        print(f"❌ Failed to sync emails: {response.status_code}")
        print(response.text)

    # Test retrieving emails from the database
    print("\nRetrieving emails from the database...")
    response = requests.get(f"{BASE_URL}/emails")

    if response.status_code == 200:
        emails = response.json()
        print(f"✅ Successfully retrieved {len(emails)} emails from the database")
        if emails:
            print("\nSample email from database:")
            print(f"From: {emails[0]['from']}")
            print(f"Subject: {emails[0]['subject']}")
            print(f"Received: {emails[0]['received_date']}")
    else:
        print(f"❌ Failed to retrieve emails: {response.status_code}")
        print(response.text)


def test_email_processing():
    """Test email processing with rules."""
    print_section("Testing Email Processing")

    # Create a test rule
    rule_data = {
        "name": "Test Processing Rule",
        "match_type": "all",
        "conditions": [
            {"field": "from", "predicate": "contains", "value": "test@example.com"},
            {"field": "subject", "predicate": "contains", "value": "Test Email"},
        ],
        "actions": [
            {"type": "mark_as_read"},
            {"type": "move_message", "target": "Test Folder"},
        ],
    }

    print("Creating a test rule for email processing...")
    response = requests.post(f"{BASE_URL}/rules", json=rule_data)

    if response.status_code == 201:
        rule = response.json()
        rule_id = rule["id"]
        print(f"✅ Test rule created with ID: {rule_id}")
    else:
        print(f"❌ Failed to create test rule: {response.status_code}")
        print(response.text)
        return

    # Create a test email that matches the rule
    test_email = {
        "from": "test@example.com",
        "to": "recipient@example.com",
        "subject": "Test Email Subject",
        "message": "This is a test email for processing.",
        "received_date": datetime.now().isoformat(),
    }

    print("\nProcessing a test email that matches the rule...")
    response = requests.post(f"{BASE_URL}/test/process-email", json=test_email)

    if response.status_code == 200:
        result = response.json()
        print("✅ Test email processed successfully")
        print("Actions to be applied:")
        for action in result.get("actions", []):
            print(
                f"  - {action['type']}"
                + (f" to {action['target']}" if "target" in action else "")
            )
    else:
        print(f"❌ Failed to process test email: {response.status_code}")
        print(response.text)

    # Create a test email that doesn't match the rule
    non_matching_email = {
        "from": "other@example.com",
        "to": "recipient@example.com",
        "subject": "Non-matching Subject",
        "message": "This email should not match the rule.",
        "received_date": datetime.now().isoformat(),
    }

    print("\nProcessing a test email that doesn't match the rule...")
    response = requests.post(f"{BASE_URL}/test/process-email", json=non_matching_email)

    if response.status_code == 200:
        result = response.json()
        actions = result.get("actions", [])
        if not actions:
            print("✅ Test email correctly did not match any rules (no actions)")
        else:
            print("❌ Test email unexpectedly matched rules:")
            for action in actions:
                print(
                    f"  - {action['type']}"
                    + (f" to {action['target']}" if "target" in action else "")
                )
    else:
        print(f"❌ Failed to process test email: {response.status_code}")
        print(response.text)

    # Clean up - delete the test rule
    print(f"\nCleaning up - deleting test rule with ID: {rule_id}...")
    response = requests.delete(f"{BASE_URL}/rules/{rule_id}")

    if response.status_code == 204:
        print("✅ Test rule deleted successfully")
    else:
        print(f"❌ Failed to delete test rule: {response.status_code}")
        print(response.text)


def test_complex_rules():
    """Test more complex rule scenarios."""
    print_section("Testing Complex Rules")

    # Create a rule with "any" match type
    any_rule_data = {
        "name": "Any Match Rule",
        "match_type": "any",
        "conditions": [
            {
                "field": "from",
                "predicate": "contains",
                "value": "important@example.com",
            },
            {"field": "subject", "predicate": "contains", "value": "Urgent"},
        ],
        "actions": [{"type": "mark_as_read"}],
    }

    print("Creating a rule with 'any' match type...")
    response = requests.post(f"{BASE_URL}/rules", json=any_rule_data)

    if response.status_code == 201:
        any_rule = response.json()
        any_rule_id = any_rule["id"]
        print(f"✅ 'Any' match rule created with ID: {any_rule_id}")
    else:
        print(f"❌ Failed to create 'any' match rule: {response.status_code}")
        print(response.text)
        return

    # Create a rule with date condition
    date_rule_data = {
        "name": "Date Condition Rule",
        "match_type": "all",
        "conditions": [
            {
                "field": "from",
                "predicate": "contains",
                "value": "newsletter@example.com",
            },
            {
                "field": "received_date",
                "predicate": "less_than",
                "value": "2",
                "unit": "days",
            },
        ],
        "actions": [{"type": "move_message", "target": "Newsletters"}],
    }

    print("\nCreating a rule with date condition...")
    response = requests.post(f"{BASE_URL}/rules", json=date_rule_data)

    if response.status_code == 201:
        date_rule = response.json()
        date_rule_id = date_rule["id"]
        print(f"✅ Date condition rule created with ID: {date_rule_id}")
    else:
        print(f"❌ Failed to create date condition rule: {response.status_code}")
        print(response.text)
        return

    # Test the "any" match rule with an email that matches one condition
    any_match_email = {
        "from": "someone@example.com",
        "to": "recipient@example.com",
        "subject": "Urgent: Please respond",
        "message": "This is an urgent message.",
        "received_date": datetime.now().isoformat(),
    }

    print("\nTesting 'any' match rule with an email that matches one condition...")
    response = requests.post(f"{BASE_URL}/test/process-email", json=any_match_email)

    if response.status_code == 200:
        result = response.json()
        actions = result.get("actions", [])
        if actions:
            print("✅ Email correctly matched 'any' rule with one condition")
            print("Actions to be applied:")
            for action in actions:
                print(
                    f"  - {action['type']}"
                    + (f" to {action['target']}" if "target" in action else "")
                )
        else:
            print("❌ Email unexpectedly did not match 'any' rule")
    else:
        print(f"❌ Failed to process test email: {response.status_code}")
        print(response.text)

    # Test the date condition rule with a recent email
    recent_email = {
        "from": "newsletter@example.com",
        "to": "recipient@example.com",
        "subject": "Weekly Newsletter",
        "message": "This is this week's newsletter.",
        "received_date": datetime.now().isoformat(),
    }

    print("\nTesting date condition rule with a recent email...")
    response = requests.post(f"{BASE_URL}/test/process-email", json=recent_email)

    if response.status_code == 200:
        result = response.json()
        actions = result.get("actions", [])
        if actions:
            print("✅ Recent email correctly matched date condition rule")
            print("Actions to be applied:")
            for action in actions:
                print(
                    f"  - {action['type']}"
                    + (f" to {action['target']}" if "target" in action else "")
                )
        else:
            print("❌ Recent email unexpectedly did not match date condition rule")
    else:
        print(f"❌ Failed to process test email: {response.status_code}")
        print(response.text)

    # Test the date condition rule with an old email
    old_date = datetime.now() - timedelta(days=5)
    old_email = {
        "from": "newsletter@example.com",
        "to": "recipient@example.com",
        "subject": "Old Newsletter",
        "message": "This is an old newsletter.",
        "received_date": old_date.isoformat(),
    }

    print("\nTesting date condition rule with an old email...")
    response = requests.post(f"{BASE_URL}/test/process-email", json=old_email)

    if response.status_code == 200:
        result = response.json()
        actions = result.get("actions", [])
        if not actions:
            print("✅ Old email correctly did not match date condition rule")
        else:
            print("❌ Old email unexpectedly matched date condition rule:")
            for action in actions:
                print(
                    f"  - {action['type']}"
                    + (f" to {action['target']}" if "target" in action else "")
                )
    else:
        print(f"❌ Failed to process test email: {response.status_code}")
        print(response.text)

    # Clean up - delete the test rules
    print(f"\nCleaning up - deleting test rules...")

    response = requests.delete(f"{BASE_URL}/rules/{any_rule_id}")
    if response.status_code == 204:
        print(f"✅ 'Any' match rule deleted successfully")
    else:
        print(f"❌ Failed to delete 'any' match rule: {response.status_code}")

    response = requests.delete(f"{BASE_URL}/rules/{date_rule_id}")
    if response.status_code == 204:
        print(f"✅ Date condition rule deleted successfully")
    else:
        print(f"❌ Failed to delete date condition rule: {response.status_code}")


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print(" EMAIL RULES ENGINE - COMPREHENSIVE TEST SUITE ".center(80, "="))
    print("=" * 80 + "\n")

    print("Starting tests...")
    print("Make sure the application is running at http://localhost:8000")

    # Check if the API is available
    try:
        response = requests.get(f"{BASE_URL}")
        if response.status_code != 200:
            print(f"❌ API is not available. Status code: {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API. Make sure the application is running.")
        return

    print("✅ API is available")

    # Run the tests
    test_rule_management()
    test_gmail_integration()
    test_email_processing()
    test_complex_rules()

    print("\n" + "=" * 80)
    print(" TEST SUITE COMPLETED ".center(80, "="))
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
