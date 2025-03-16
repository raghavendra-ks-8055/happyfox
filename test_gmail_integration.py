import requests
import json

# Base URL for the API
base_url = "http://localhost:8000/api"


# Test fetching emails from Gmail
def test_fetch_emails():
    response = requests.get(f"{base_url}/gmail/messages?max_results=5")
    if response.status_code == 200:
        emails = response.json()
        print(f"Successfully fetched {len(emails)} emails from Gmail")
        return emails
    else:
        print(f"Failed to fetch emails: {response.status_code}")
        return None


# Test fetching emails using the API endpoint
def test_fetch_emails_api():
    # Test API method
    response = requests.get(f"{base_url}/gmail/fetch?method=api&max_results=5")
    if response.status_code == 200:
        emails = response.json()
        print(f"Successfully fetched {len(emails)} emails using API method")
        return emails
    else:
        print(f"Failed to fetch emails using API method: {response.status_code}")
        return None


# Test syncing emails to the database
def test_sync_emails():
    response = requests.post(f"{base_url}/gmail/sync?max_results=5")
    if response.status_code == 200:
        emails = response.json()
        print(f"Successfully synced {len(emails)} emails to the database")
        return emails
    else:
        print(f"Failed to sync emails: {response.status_code}")
        return None


# Test retrieving emails from the database
def test_get_emails():
    response = requests.get(f"{base_url}/emails")
    if response.status_code == 200:
        emails = response.json()
        print(f"Successfully retrieved {len(emails)} emails from the database")
        return emails
    else:
        print(f"Failed to retrieve emails: {response.status_code}")
        return None


# Test creating a test email
def test_create_test_email():
    test_email_data = {
        "from_email": "test@example.com",
        "to_email": "recipient@example.com",
        "subject": "Test Email Subject",
        "body": "This is a test email body created for testing purposes.",
    }

    response = requests.post(f"{base_url}/test/email", params=test_email_data)

    if response.status_code == 201:
        email = response.json()
        print(f"Successfully created test email with ID: {email.get('id')}")
        print(f"Actions to be applied: {email.get('actions', [])}")
        return email
    else:
        print(f"Failed to create test email: {response.status_code}")
        return None


# Test processing an email without storing it
def test_process_email():
    test_email = {
        "from": "sender@example.com",
        "to": "recipient@example.com",
        "subject": "Test Processing Email",
        "message": "This is a test email for processing against rules.",
    }

    response = requests.post(f"{base_url}/test/process-email", json=test_email)

    if response.status_code == 200:
        result = response.json()
        print(f"Successfully processed test email")
        print(f"Actions to be applied: {result.get('actions', [])}")
        return result
    else:
        print(f"Failed to process test email: {response.status_code}")
        return None


# Run the tests
if __name__ == "__main__":
    print("Testing Gmail API integration...")
    fetched_emails = test_fetch_emails()
    api_emails = test_fetch_emails_api()
    synced_emails = test_sync_emails()
    stored_emails = test_get_emails()

    # Print a sample email
    if stored_emails and len(stored_emails) > 0:
        print("\nSample email from database:")
        print(json.dumps(stored_emails[0], indent=2))

    print("\nTesting test email API...")
    test_email = test_create_test_email()
    processed_email = test_process_email()

    # Print test email results
    if test_email:
        print("\nCreated test email:")
        print(json.dumps(test_email, indent=2))

    if processed_email:
        print("\nProcessed test email:")
        print(json.dumps(processed_email, indent=2))
