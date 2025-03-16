from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.rule import Rule, Condition, Action
from app.schemas.rule import RuleCreate, RuleUpdate


class RuleService:
    """
    Service for managing rules.
    """

    @staticmethod
    def get_rules(db: Session, skip: int = 0, limit: int = 100) -> List[Rule]:
        """
        Get all rules.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Rule]: List of rules
        """
        return db.query(Rule).offset(skip).limit(limit).all()

    @staticmethod
    def get_rule(db: Session, rule_id: UUID) -> Optional[Rule]:
        """
        Get a rule by ID.

        Args:
            db: Database session
            rule_id: ID of the rule to get

        Returns:
            Optional[Rule]: The rule if found, None otherwise
        """
        return db.query(Rule).filter(Rule.id == rule_id).first()

    @staticmethod
    def create_rule(db: Session, rule_in: RuleCreate) -> Rule:
        """
        Create a new rule.

        Args:
            db: Database session
            rule_in: Rule data

        Returns:
            Rule: The created rule
        """
        # Create the rule
        db_rule = Rule(name=rule_in.name, match_type=rule_in.match_type)
        db.add(db_rule)
        db.flush()  # Flush to get the rule ID

        # Create conditions
        for condition_in in rule_in.conditions:
            db_condition = Condition(
                rule_id=db_rule.id,
                field=condition_in.field,
                predicate=condition_in.predicate,
                value=condition_in.value,
                unit=condition_in.unit,
            )
            db.add(db_condition)

        # Create actions
        for action_in in rule_in.actions:
            db_action = Action(
                rule_id=db_rule.id, type=action_in.type, target=action_in.target
            )
            db.add(db_action)

        db.commit()
        db.refresh(db_rule)
        return db_rule

    @staticmethod
    def update_rule(db: Session, rule_id: UUID, rule_in: RuleUpdate) -> Optional[Rule]:
        """
        Update a rule.

        Args:
            db: Database session
            rule_id: ID of the rule to update
            rule_in: Updated rule data

        Returns:
            Optional[Rule]: The updated rule if found, None otherwise
        """
        db_rule = RuleService.get_rule(db, rule_id)
        if not db_rule:
            return None

        # Update rule fields
        if rule_in.name is not None:
            db_rule.name = rule_in.name
        if rule_in.match_type is not None:
            db_rule.match_type = rule_in.match_type

        # Update conditions if provided
        if rule_in.conditions is not None:
            # Delete existing conditions
            db.query(Condition).filter(Condition.rule_id == rule_id).delete()

            # Create new conditions
            for condition_in in rule_in.conditions:
                db_condition = Condition(
                    rule_id=db_rule.id,
                    field=condition_in.field,
                    predicate=condition_in.predicate,
                    value=condition_in.value,
                    unit=condition_in.unit,
                )
                db.add(db_condition)

        # Update actions if provided
        if rule_in.actions is not None:
            # Delete existing actions
            db.query(Action).filter(Action.rule_id == rule_id).delete()

            # Create new actions
            for action_in in rule_in.actions:
                db_action = Action(
                    rule_id=db_rule.id, type=action_in.type, target=action_in.target
                )
                db.add(db_action)

        db.commit()
        db.refresh(db_rule)
        return db_rule

    @staticmethod
    def delete_rule(db: Session, rule_id: UUID) -> bool:
        """
        Delete a rule.

        Args:
            db: Database session
            rule_id: ID of the rule to delete

        Returns:
            bool: True if the rule was deleted, False otherwise
        """
        db_rule = RuleService.get_rule(db, rule_id)
        if not db_rule:
            return False

        db.delete(db_rule)
        db.commit()
        return True
