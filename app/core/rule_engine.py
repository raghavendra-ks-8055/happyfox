from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from app.models.rule import Rule


class RuleEngine:
    """
    Core rule engine for processing email rules.
    """

    @staticmethod
    def evaluate_condition(condition: Dict[str, Any], email: Dict[str, Any]) -> bool:
        """
        Evaluate a single condition against an email.

        Args:
            condition: The condition to evaluate
            email: The email data to check against

        Returns:
            bool: True if the condition matches, False otherwise
        """
        field = condition["field"]
        predicate = condition["predicate"]
        value = condition["value"]

        # Get the field value from the email
        if field == "from":
            field_value = email.get("from", "")
        elif field == "subject":
            field_value = email.get("subject", "")
        elif field == "message":
            field_value = email.get("message", "")
        elif field == "received_date":
            field_value = email.get("received_date", datetime.utcnow())
        else:
            return False

        # Evaluate the predicate
        if predicate == "contains":
            return value.lower() in str(field_value).lower()
        elif predicate == "does_not_contain":
            return value.lower() not in str(field_value).lower()
        elif predicate == "equals":
            return str(field_value).lower() == value.lower()
        elif predicate == "does_not_equal":
            return str(field_value).lower() != value.lower()
        elif predicate in ["less_than", "greater_than"] and field == "received_date":
            # Handle date comparisons
            unit = condition.get("unit", "days")
            value_int = int(value)

            if unit == "days":
                threshold_date = datetime.utcnow() - timedelta(days=value_int)
            elif unit == "months":
                # Approximate months as 30 days
                threshold_date = datetime.utcnow() - timedelta(days=30 * value_int)
            else:
                return False

            if predicate == "less_than":
                return field_value > threshold_date
            else:  # greater_than
                return field_value < threshold_date

        return False

    @staticmethod
    def evaluate_rule(rule: Rule, email: Dict[str, Any]) -> bool:
        """
        Evaluate a rule against an email.

        Args:
            rule: The rule to evaluate
            email: The email data to check against

        Returns:
            bool: True if the rule matches, False otherwise
        """
        if not rule.conditions:
            return False

        # Convert SQLAlchemy objects to dictionaries
        conditions = [
            {
                "field": condition.field,
                "predicate": condition.predicate,
                "value": condition.value,
                "unit": condition.unit,
            }
            for condition in rule.conditions
        ]

        # Evaluate conditions based on match_type
        if rule.match_type == "all":
            return all(
                RuleEngine.evaluate_condition(condition, email)
                for condition in conditions
            )
        else:  # any
            return any(
                RuleEngine.evaluate_condition(condition, email)
                for condition in conditions
            )

    @staticmethod
    def get_actions(rule: Rule) -> List[Dict[str, Any]]:
        """
        Get the actions for a rule.

        Args:
            rule: The rule to get actions for

        Returns:
            List[Dict[str, Any]]: The actions to perform
        """
        return [
            {"type": action.type, "target": action.target} for action in rule.actions
        ]

    @staticmethod
    def process_email(rules: List[Rule], email: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process an email against a list of rules.

        Args:
            rules: The rules to evaluate
            email: The email data to check against

        Returns:
            List[Dict[str, Any]]: The actions to perform
        """
        actions = []

        for rule in rules:
            if RuleEngine.evaluate_rule(rule, email):
                actions.extend(RuleEngine.get_actions(rule))

        return actions
