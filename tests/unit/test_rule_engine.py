import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from app.core.rule_engine import RuleEngine
from app.models.rule import Rule, Condition, Action


class TestRuleEngine(unittest.TestCase):
    def setUp(self):
        # Create a mock rule with conditions and actions
        self.rule = MagicMock(spec=Rule)
        self.rule.match_type = "all"

        # Create conditions
        condition1 = MagicMock(spec=Condition)
        condition1.field = "from"
        condition1.predicate = "contains"
        condition1.value = "tenmiles.com"
        condition1.unit = None

        condition2 = MagicMock(spec=Condition)
        condition2.field = "subject"
        condition2.predicate = "contains"
        condition2.value = "Interview"
        condition2.unit = None

        condition3 = MagicMock(spec=Condition)
        condition3.field = "received_date"
        condition3.predicate = "less_than"
        condition3.value = "2"
        condition3.unit = "days"

        self.rule.conditions = [condition1, condition2, condition3]

        # Create actions
        action1 = MagicMock(spec=Action)
        action1.type = "move_message"
        action1.target = "Inbox"

        action2 = MagicMock(spec=Action)
        action2.type = "mark_as_read"
        action2.target = None

        self.rule.actions = [action1, action2]

        # Create test email
        self.email = {
            "from": "test@tenmiles.com",
            "subject": "Interview Schedule",
            "message": "We would like to schedule an interview with you.",
            "received_date": datetime.utcnow() - timedelta(hours=12),
        }

    def test_evaluate_condition_contains(self):
        condition = {"field": "from", "predicate": "contains", "value": "tenmiles.com"}
        result = RuleEngine.evaluate_condition(condition, self.email)
        self.assertTrue(result)

        condition["value"] = "example.com"
        result = RuleEngine.evaluate_condition(condition, self.email)
        self.assertFalse(result)

    def test_evaluate_condition_does_not_contain(self):
        condition = {
            "field": "from",
            "predicate": "does_not_contain",
            "value": "example.com",
        }
        result = RuleEngine.evaluate_condition(condition, self.email)
        self.assertTrue(result)

        condition["value"] = "tenmiles.com"
        result = RuleEngine.evaluate_condition(condition, self.email)
        self.assertFalse(result)

    def test_evaluate_condition_equals(self):
        condition = {
            "field": "from",
            "predicate": "equals",
            "value": "test@tenmiles.com",
        }
        result = RuleEngine.evaluate_condition(condition, self.email)
        self.assertTrue(result)

        condition["value"] = "other@tenmiles.com"
        result = RuleEngine.evaluate_condition(condition, self.email)
        self.assertFalse(result)

    def test_evaluate_condition_does_not_equal(self):
        condition = {
            "field": "from",
            "predicate": "does_not_equal",
            "value": "other@tenmiles.com",
        }
        result = RuleEngine.evaluate_condition(condition, self.email)
        self.assertTrue(result)

        condition["value"] = "test@tenmiles.com"
        result = RuleEngine.evaluate_condition(condition, self.email)
        self.assertFalse(result)

    def test_evaluate_condition_less_than(self):
        condition = {
            "field": "received_date",
            "predicate": "less_than",
            "value": "2",
            "unit": "days",
        }
        result = RuleEngine.evaluate_condition(condition, self.email)
        self.assertTrue(result)

        condition["value"] = "0.1"  # Less than 0.1 days (2.4 hours)
        result = RuleEngine.evaluate_condition(condition, self.email)
        self.assertFalse(result)

    def test_evaluate_condition_greater_than(self):
        condition = {
            "field": "received_date",
            "predicate": "greater_than",
            "value": "0.1",  # Greater than 0.1 days (2.4 hours)
            "unit": "days",
        }
        result = RuleEngine.evaluate_condition(condition, self.email)
        self.assertTrue(result)

        condition["value"] = "2"  # Greater than 2 days
        result = RuleEngine.evaluate_condition(condition, self.email)
        self.assertFalse(result)

    def test_evaluate_rule_all_match(self):
        result = RuleEngine.evaluate_rule(self.rule, self.email)
        self.assertTrue(result)

    def test_evaluate_rule_one_mismatch(self):
        # Change one condition to make it not match
        self.rule.conditions[1].value = "Meeting"
        result = RuleEngine.evaluate_rule(self.rule, self.email)
        self.assertFalse(result)

    def test_evaluate_rule_any_match(self):
        self.rule.match_type = "any"

        # Make one condition not match
        self.rule.conditions[1].value = "Meeting"
        result = RuleEngine.evaluate_rule(self.rule, self.email)
        self.assertTrue(result)

        # Make all conditions not match
        self.rule.conditions[0].value = "example.com"
        self.rule.conditions[2].value = "0.1"
        result = RuleEngine.evaluate_rule(self.rule, self.email)
        self.assertFalse(result)

    def test_get_actions(self):
        actions = RuleEngine.get_actions(self.rule)
        self.assertEqual(len(actions), 2)
        self.assertEqual(actions[0]["type"], "move_message")
        self.assertEqual(actions[0]["target"], "Inbox")
        self.assertEqual(actions[1]["type"], "mark_as_read")
        self.assertIsNone(actions[1]["target"])

    def test_process_email(self):
        rules = [self.rule]
        actions = RuleEngine.process_email(rules, self.email)
        self.assertEqual(len(actions), 2)
        self.assertEqual(actions[0]["type"], "move_message")
        self.assertEqual(actions[0]["target"], "Inbox")
        self.assertEqual(actions[1]["type"], "mark_as_read")
        self.assertIsNone(actions[1]["target"])

        # Make the rule not match
        self.rule.conditions[0].value = "example.com"
        actions = RuleEngine.process_email(rules, self.email)
        self.assertEqual(len(actions), 0)


if __name__ == "__main__":
    unittest.main()
