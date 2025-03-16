import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Email(Base):
    __tablename__ = "emails"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    gmail_id = Column(String, unique=True, index=True, nullable=False)
    thread_id = Column(String, index=True)
    from_address = Column(String, nullable=False)
    to_address = Column(String)
    subject = Column(String)
    body = Column(Text)
    snippet = Column(String)
    received_date = Column(DateTime, default=datetime.utcnow)
    label_ids = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Email {self.subject}>"

    def to_dict(self):
        """
        Convert the Email model to a dictionary.

        Returns:
            dict: Dictionary representation of the Email model
        """
        return {
            "id": str(self.id),
            "gmail_id": self.gmail_id,
            "thread_id": self.thread_id,
            "from": self.from_address,
            "to": self.to_address,
            "subject": self.subject,
            "message": self.body,
            "snippet": self.snippet,
            "received_date": self.received_date,
            "label_ids": self.label_ids,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
