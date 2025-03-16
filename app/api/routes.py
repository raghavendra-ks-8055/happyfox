from typing import List, Dict, Any
from uuid import UUID
import uuid
from datetime import datetime
import os
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.rule_engine import RuleEngine
from app.models.rule import Rule
from app.models.email import Email
from app.schemas.rule import Rule as RuleSchema, RuleCreate, RuleUpdate
from app.services.rule import RuleService
from app.services.email import EmailService

# Create API router
api_router = APIRouter()


# Add Gmail OAuth routes
@api_router.get("/gmail/authorize")
async def gmail_authorize():
    """
    Start the Gmail OAuth flow.

    This endpoint provides instructions for setting up Gmail OAuth.
    """
    return {
        "message": "Gmail OAuth Setup Instructions",
        "steps": [
            "1. Run the setup_gmail_oauth.py script in your terminal: python3 setup_gmail_oauth.py",
            "2. Follow the instructions in the terminal",
            "3. A browser window will open for you to authorize the application",
            "4. After authorization, the credentials will be saved to token.json",
            "5. You can then use the Gmail API endpoints",
        ],
        "note": "The OAuth flow cannot be completed through this API endpoint due to technical limitations. Please use the provided script instead.",
    }


@api_router.get("/rules", response_model=List[RuleSchema])
def get_rules(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all rules.
    """
    rules = RuleService.get_rules(db, skip=skip, limit=limit)
    return rules


@api_router.get("/rules/{rule_id}", response_model=RuleSchema)
def get_rule(rule_id: UUID, db: Session = Depends(get_db)):
    """
    Get a rule by ID.
    """
    rule = RuleService.get_rule(db, rule_id=rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found"
        )
    return rule


@api_router.post(
    "/rules", response_model=RuleSchema, status_code=status.HTTP_201_CREATED
)
def create_rule(rule_in: RuleCreate, db: Session = Depends(get_db)):
    """
    Create a new rule.
    """
    rule = RuleService.create_rule(db, rule_in=rule_in)
    return rule


@api_router.put("/rules/{rule_id}", response_model=RuleSchema)
def update_rule(rule_id: UUID, rule_in: RuleUpdate, db: Session = Depends(get_db)):
    """
    Update a rule.
    """
    rule = RuleService.update_rule(db, rule_id=rule_id, rule_in=rule_in)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found"
        )
    return rule


@api_router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(rule_id: UUID, db: Session = Depends(get_db)):
    """
    Delete a rule.
    """
    success = RuleService.delete_rule(db, rule_id=rule_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found"
        )
    return None


@api_router.post("/process-email", response_model=List[Dict[str, Any]])
def process_email(email: Dict[str, Any], db: Session = Depends(get_db)):
    """
    Process an email against all rules.

    Example request body:
    ```json
    {
        "from": "example@tenmiles.com",
        "subject": "Interview Invitation",
        "message": "We would like to invite you for an interview.",
        "received_date": "2023-11-01T12:00:00"
    }
    ```
    """
    # Parse received_date if it's a string
    if isinstance(email.get("received_date"), str):
        from datetime import datetime

        try:
            email["received_date"] = datetime.fromisoformat(email["received_date"])
        except (ValueError, TypeError):
            email["received_date"] = datetime.utcnow()

    # Get all rules
    rules = RuleService.get_rules(db)

    # Process email against rules
    actions = RuleEngine.process_email(rules, email)

    return actions


@api_router.get("/gmail/messages", response_model=List[Dict[str, Any]])
def get_gmail_messages(
    max_results: int = 10, query: str = "in:inbox", db: Session = Depends(get_db)
):
    """
    Fetch messages from Gmail inbox using the Gmail API.

    Args:
        max_results: Maximum number of messages to return
        query: Gmail search query
        db: Database session

    Returns:
        List[Dict[str, Any]]: List of messages
    """
    from app.services.gmail_service import GmailService

    # Fetch messages from Gmail
    messages = GmailService.list_messages(max_results=max_results, query=query)

    # Process messages against rules
    processed_messages = []
    for message in messages:
        # Get all rules
        rules = RuleService.get_rules(db)

        # Process email against rules
        actions = RuleEngine.process_email(rules, message)

        # Add actions to the message
        message["actions"] = actions
        processed_messages.append(message)

    return processed_messages


@api_router.get("/gmail/fetch", response_model=List[Dict[str, Any]])
def fetch_gmail_messages(
    max_results: int = 10,
    query: str = "in:inbox",
    db: Session = Depends(get_db),
):
    """
    Fetch messages from Gmail using the API.

    Args:
        max_results: Maximum number of messages to return
        query: Gmail search query
        db: Database session

    Returns:
        List[Dict[str, Any]]: List of messages
    """
    from app.services.gmail_service import GmailService

    # Fetch messages from Gmail
    messages = GmailService.fetch_emails(max_results=max_results, query=query)

    # Process messages against rules
    processed_messages = []
    for message in messages:
        # Get all rules
        rules = RuleService.get_rules(db)

        # Process email against rules
        actions = RuleEngine.process_email(rules, message)

        # Add actions to the message
        message["actions"] = actions
        processed_messages.append(message)

    return processed_messages


@api_router.post("/gmail/sync", response_model=List[Dict[str, Any]])
def sync_gmail_messages(
    max_results: int = 10, query: str = "in:inbox", db: Session = Depends(get_db)
):
    """
    Fetch messages from Gmail inbox and store them in the database.

    Args:
        max_results: Maximum number of messages to return
        query: Gmail search query
        db: Database session

    Returns:
        List[Dict[str, Any]]: List of stored messages
    """
    from app.services.gmail_service import GmailService

    # Fetch messages from Gmail
    messages = GmailService.list_messages(max_results=max_results, query=query)

    # Store messages in database
    stored_messages = []
    for message in messages:
        email = EmailService.create_email(db, message)

        # Convert SQLAlchemy model to dict
        email_dict = {
            "id": str(email.id),
            "gmail_id": email.gmail_id,
            "thread_id": email.thread_id,
            "from": email.from_address,
            "to": email.to_address,
            "subject": email.subject,
            "body": email.body,
            "snippet": email.snippet,
            "received_date": email.received_date,
            "label_ids": email.label_ids,
            "created_at": email.created_at,
            "updated_at": email.updated_at,
        }

        stored_messages.append(email_dict)

    return stored_messages


@api_router.get("/emails", response_model=List[Dict[str, Any]])
def get_emails(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all emails from the database.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session

    Returns:
        List[Dict[str, Any]]: List of emails
    """
    emails = EmailService.get_emails(db, skip=skip, limit=limit)

    # Convert SQLAlchemy models to dicts
    email_dicts = []
    for email in emails:
        email_dict = {
            "id": str(email.id),
            "gmail_id": email.gmail_id,
            "thread_id": email.thread_id,
            "from": email.from_address,
            "to": email.to_address,
            "subject": email.subject,
            "body": email.body,
            "snippet": email.snippet,
            "received_date": email.received_date,
            "label_ids": email.label_ids,
            "created_at": email.created_at,
            "updated_at": email.updated_at,
        }
        email_dicts.append(email_dict)

    return email_dicts


@api_router.get("/emails/{email_id}", response_model=Dict[str, Any])
def get_email(email_id: str, db: Session = Depends(get_db)):
    """
    Get an email by ID.

    Args:
        email_id: Email ID
        db: Database session

    Returns:
        Dict[str, Any]: Email data
    """
    email = EmailService.get_email_by_id(db, email_id)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Email with ID {email_id} not found",
        )

    # Convert SQLAlchemy model to dict
    email_dict = {
        "id": str(email.id),
        "gmail_id": email.gmail_id,
        "thread_id": email.thread_id,
        "from": email.from_address,
        "to": email.to_address,
        "subject": email.subject,
        "body": email.body,
        "snippet": email.snippet,
        "received_date": email.received_date,
        "label_ids": email.label_ids,
        "created_at": email.created_at,
        "updated_at": email.updated_at,
    }

    return email_dict


# Add new test email endpoints
@api_router.post(
    "/test/email", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED
)
def test_create_email(
    from_email: str,
    to_email: str,
    subject: str,
    body: str,
    db: Session = Depends(get_db),
):
    """
    Create a test email in the database.

    This endpoint allows you to create a test email without actually sending it.
    The email will be stored in the database and can be processed by rules.

    Args:
        from_email: The sender's email address
        to_email: The recipient's email address
        subject: The email subject
        body: The email body
        db: Database session

    Returns:
        Dict[str, Any]: The created email
    """
    # Create a test email object
    email_data = {
        "id": str(uuid.uuid4()),
        "thread_id": str(uuid.uuid4()),
        "label_ids": ["INBOX"],
        "snippet": body[:100] + "..." if len(body) > 100 else body,
        "from": from_email,
        "to": to_email,
        "subject": subject,
        "date": datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z"),
        "received_date": datetime.now(),
        "message": body,
    }

    # Store the email in the database
    email = EmailService.create_email(db, email_data)

    # Process the email against rules
    rules = RuleService.get_rules(db)
    actions = RuleEngine.process_email(rules, email_data)

    # Add actions to the response
    result = email.to_dict()
    result["actions"] = actions

    return result


@api_router.post("/test/process-email", response_model=Dict[str, Any])
def test_process_email(email: Dict[str, Any], db: Session = Depends(get_db)):
    """
    Test processing an email against rules without storing it.

    This endpoint allows you to test how an email would be processed by the rules
    without actually storing it in the database.

    Args:
        email: The email data to process
        db: Database session

    Returns:
        Dict[str, Any]: The email with actions that would be applied
    """
    # Ensure required fields are present
    required_fields = ["from", "subject", "message"]
    for field in required_fields:
        if field not in email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required field: {field}",
            )

    # Add default values for missing fields
    if "received_date" not in email:
        email["received_date"] = datetime.now()

    # Get all rules
    rules = RuleService.get_rules(db)

    # Process email against rules
    actions = RuleEngine.process_email(rules, email)

    # Add actions to the email
    email["actions"] = actions

    return email
