import uuid
from datetime import datetime
from typing import List

from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Rule(Base):
    __tablename__ = "rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    match_type = Column(Enum("all", "any", name="match_type"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    conditions = relationship(
        "Condition", back_populates="rule", cascade="all, delete-orphan"
    )
    actions = relationship(
        "Action", back_populates="rule", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Rule {self.name}>"


class Condition(Base):
    __tablename__ = "conditions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_id = Column(UUID(as_uuid=True), ForeignKey("rules.id"), nullable=False)
    field = Column(
        Enum("from", "subject", "message", "received_date", name="field_type"),
        nullable=False,
    )
    predicate = Column(
        Enum(
            "contains",
            "does_not_contain",
            "equals",
            "does_not_equal",
            "less_than",
            "greater_than",
            name="predicate_type",
        ),
        nullable=False,
    )
    value = Column(String, nullable=False)
    unit = Column(String, nullable=True)  # For date predicates (days, months)

    # Relationships
    rule = relationship("Rule", back_populates="conditions")

    def __repr__(self):
        return f"<Condition {self.field} {self.predicate} {self.value}>"


class Action(Base):
    __tablename__ = "actions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_id = Column(UUID(as_uuid=True), ForeignKey("rules.id"), nullable=False)
    type = Column(
        Enum("mark_as_read", "mark_as_unread", "move_message", name="action_type"),
        nullable=False,
    )
    target = Column(String, nullable=True)  # For move_message action

    # Relationships
    rule = relationship("Rule", back_populates="actions")

    def __repr__(self):
        return f"<Action {self.type}>"
