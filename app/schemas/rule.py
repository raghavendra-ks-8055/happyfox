from datetime import datetime
from typing import List, Optional, Literal
from uuid import UUID

from pydantic import BaseModel, Field


# Condition Schemas
class ConditionBase(BaseModel):
    field: Literal["from", "subject", "message", "received_date"]
    predicate: Literal[
        "contains",
        "does_not_contain",
        "equals",
        "does_not_equal",
        "less_than",
        "greater_than",
    ]
    value: str
    unit: Optional[str] = None  # For date predicates (days, months)


class ConditionCreate(ConditionBase):
    pass


class ConditionUpdate(ConditionBase):
    field: Optional[Literal["from", "subject", "message", "received_date"]] = None
    predicate: Optional[
        Literal[
            "contains",
            "does_not_contain",
            "equals",
            "does_not_equal",
            "less_than",
            "greater_than",
        ]
    ] = None
    value: Optional[str] = None


class ConditionInDBBase(ConditionBase):
    id: UUID
    rule_id: UUID

    class Config:
        from_attributes = True


class Condition(ConditionInDBBase):
    pass


# Action Schemas
class ActionBase(BaseModel):
    type: Literal["mark_as_read", "mark_as_unread", "move_message"]
    target: Optional[str] = None  # For move_message action


class ActionCreate(ActionBase):
    pass


class ActionUpdate(ActionBase):
    type: Optional[Literal["mark_as_read", "mark_as_unread", "move_message"]] = None


class ActionInDBBase(ActionBase):
    id: UUID
    rule_id: UUID

    class Config:
        from_attributes = True


class Action(ActionInDBBase):
    pass


# Rule Schemas
class RuleBase(BaseModel):
    name: str
    match_type: Literal["all", "any"]


class RuleCreate(RuleBase):
    conditions: List[ConditionCreate]
    actions: List[ActionCreate]


class RuleUpdate(BaseModel):
    name: Optional[str] = None
    match_type: Optional[Literal["all", "any"]] = None
    conditions: Optional[List[ConditionCreate]] = None
    actions: Optional[List[ActionCreate]] = None


class RuleInDBBase(RuleBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Rule(RuleInDBBase):
    conditions: List[Condition]
    actions: List[Action]
