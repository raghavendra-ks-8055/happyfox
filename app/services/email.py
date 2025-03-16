from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.email import Email


class EmailService:
    """Service for handling email operations."""

    @staticmethod
    def create_email(db: Session, email_data: Dict[str, Any]) -> Email:
        """
        Create a new email record in the database.

        Args:
            db: Database session
            email_data: Email data from Gmail API

        Returns:
            Email: Created email object
        """
        # Check if email already exists
        existing_email = (
            db.query(Email).filter(Email.gmail_id == email_data["id"]).first()
        )
        if existing_email:
            return existing_email

        # Create new email object
        email = Email(
            gmail_id=email_data["id"],
            thread_id=email_data.get("thread_id", ""),
            from_address=email_data.get("from", ""),
            to_address=email_data.get("to", ""),
            subject=email_data.get("subject", ""),
            body=email_data.get("message", ""),
            snippet=email_data.get("snippet", ""),
            label_ids=email_data.get("label_ids", []),
            received_date=email_data.get("received_date", datetime.utcnow()),
        )

        # Add to database
        db.add(email)
        db.commit()
        db.refresh(email)

        return email

    @staticmethod
    def get_emails(db: Session, skip: int = 0, limit: int = 100) -> List[Email]:
        """
        Get all emails from the database.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Email]: List of emails
        """
        return db.query(Email).offset(skip).limit(limit).all()

    @staticmethod
    def get_email_by_id(db: Session, email_id: str) -> Optional[Email]:
        """
        Get an email by ID.

        Args:
            db: Database session
            email_id: Email ID

        Returns:
            Optional[Email]: Email object if found, None otherwise
        """
        return db.query(Email).filter(Email.id == email_id).first()

    @staticmethod
    def get_email_by_gmail_id(db: Session, gmail_id: str) -> Optional[Email]:
        """
        Get an email by Gmail ID.

        Args:
            db: Database session
            gmail_id: Gmail ID

        Returns:
            Optional[Email]: Email object if found, None otherwise
        """
        return db.query(Email).filter(Email.gmail_id == gmail_id).first()

    @staticmethod
    def delete_email(db: Session, email_id: str) -> bool:
        """
        Delete an email by ID.

        Args:
            db: Database session
            email_id: Email ID

        Returns:
            bool: True if deleted, False otherwise
        """
        email = db.query(Email).filter(Email.id == email_id).first()
        if email:
            db.delete(email)
            db.commit()
            return True
        return False
