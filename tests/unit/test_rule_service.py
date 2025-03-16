import unittest
from unittest.mock import MagicMock, patch
from uuid import uuid4

from app.models.rule import Rule, Condition, Action
from app.schemas.rule import RuleCreate, RuleUpdate, ConditionCreate, ActionCreate
from app.services.rule import RuleService


class TestRuleService(unittest.TestCase):
    def setUp(self):
        # Create a mock database session
        self.db = MagicMock()

        # Create a mock rule
        self.rule_id = uuid4()
        self.rule = MagicMock(spec=Rule)
        self.rule.id = self.rule_id
        self.rule.name = "Test Rule"
        self.rule.match_type = "all"

        # Create mock conditions
        condition1 = MagicMock(spec=Condition)
        condition1.id = uuid4()
        condition1.rule_id = self.rule_id
        condition1.field = "from"
        condition1.predicate = "contains"
        condition1.value = "tenmiles.com"
        condition1.unit = None

        condition2 = MagicMock(spec=Condition)
        condition2.id = uuid4()
        condition2.rule_id = self.rule_id
        condition2.field = "subject"
        condition2.predicate = "contains"
        condition2.value = "Interview"
        condition2.unit = None

        self.rule.conditions = [condition1, condition2]

        # Create mock actions
        action1 = MagicMock(spec=Action)
        action1.id = uuid4()
        action1.rule_id = self.rule_id
        action1.type = "move_message"
        action1.target = "Inbox"

        action2 = MagicMock(spec=Action)
        action2.id = uuid4()
        action2.rule_id = self.rule_id
        action2.type = "mark_as_read"
        action2.target = None

        self.rule.actions = [action1, action2]

    def test_get_rules(self):
        # Mock the database query
        self.db.query.return_value.offset.return_value.limit.return_value.all.return_value = [
            self.rule
        ]

        # Call the service method
        rules = RuleService.get_rules(self.db)

        # Verify the result
        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0], self.rule)

        # Verify the database query
        self.db.query.assert_called_once_with(Rule)
        self.db.query.return_value.offset.assert_called_once_with(0)
        self.db.query.return_value.offset.return_value.limit.assert_called_once_with(
            100
        )

    def test_get_rule(self):
        # Mock the database query
        self.db.query.return_value.filter.return_value.first.return_value = self.rule

        # Call the service method
        rule = RuleService.get_rule(self.db, self.rule_id)

        # Verify the result
        self.assertEqual(rule, self.rule)

        # Verify the database query
        self.db.query.assert_called_once_with(Rule)
        self.db.query.return_value.filter.assert_called_once()

    def test_create_rule(self):
        # Create a rule creation schema
        rule_in = RuleCreate(
            name="Test Rule",
            match_type="all",
            conditions=[
                ConditionCreate(
                    field="from", predicate="contains", value="tenmiles.com"
                ),
                ConditionCreate(
                    field="subject", predicate="contains", value="Interview"
                ),
            ],
            actions=[
                ActionCreate(type="move_message", target="Inbox"),
                ActionCreate(type="mark_as_read"),
            ],
        )

        # Mock the database operations
        self.db.add = MagicMock()
        self.db.flush = MagicMock()
        self.db.commit = MagicMock()
        self.db.refresh = MagicMock()

        # Mock the Rule constructor
        with patch("app.services.rule.Rule") as MockRule:
            MockRule.return_value = self.rule

            # Mock the Condition constructor
            with patch("app.services.rule.Condition") as MockCondition:
                # Mock the Action constructor
                with patch("app.services.rule.Action") as MockAction:
                    # Call the service method
                    rule = RuleService.create_rule(self.db, rule_in)

                    # Verify the result
                    self.assertEqual(rule, self.rule)

                    # Verify the database operations
                    self.assertEqual(
                        self.db.add.call_count, 5
                    )  # 1 rule + 2 conditions + 2 actions
                    self.db.flush.assert_called_once()
                    self.db.commit.assert_called_once()
                    self.db.refresh.assert_called_once_with(self.rule)

    def test_update_rule(self):
        # Create a rule update schema
        rule_in = RuleUpdate(
            name="Updated Rule",
            match_type="any",
            conditions=[
                ConditionCreate(field="from", predicate="contains", value="example.com")
            ],
            actions=[ActionCreate(type="mark_as_unread")],
        )

        # Mock the get_rule method
        with patch.object(RuleService, "get_rule", return_value=self.rule):
            # Mock the database operations
            self.db.add = MagicMock()
            self.db.commit = MagicMock()
            self.db.refresh = MagicMock()
            self.db.query.return_value.filter.return_value.delete = MagicMock()

            # Mock the Condition constructor
            with patch("app.services.rule.Condition") as MockCondition:
                # Mock the Action constructor
                with patch("app.services.rule.Action") as MockAction:
                    # Call the service method
                    rule = RuleService.update_rule(self.db, self.rule_id, rule_in)

                    # Verify the result
                    self.assertEqual(rule, self.rule)
                    self.assertEqual(rule.name, "Updated Rule")
                    self.assertEqual(rule.match_type, "any")

                    # Verify the database operations
                    self.assertEqual(
                        self.db.add.call_count, 2
                    )  # 1 condition + 1 action
                    self.db.commit.assert_called_once()
                    self.db.refresh.assert_called_once_with(self.rule)
                    self.assertEqual(
                        self.db.query.call_count, 2
                    )  # 1 for conditions + 1 for actions

    def test_delete_rule(self):
        # Mock the get_rule method
        with patch.object(RuleService, "get_rule", return_value=self.rule):
            # Mock the database operations
            self.db.delete = MagicMock()
            self.db.commit = MagicMock()

            # Call the service method
            result = RuleService.delete_rule(self.db, self.rule_id)

            # Verify the result
            self.assertTrue(result)

            # Verify the database operations
            self.db.delete.assert_called_once_with(self.rule)
            self.db.commit.assert_called_once()

    def test_delete_rule_not_found(self):
        # Mock the get_rule method to return None
        with patch.object(RuleService, "get_rule", return_value=None):
            # Call the service method
            result = RuleService.delete_rule(self.db, self.rule_id)

            # Verify the result
            self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
