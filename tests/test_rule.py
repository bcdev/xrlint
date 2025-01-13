import unittest
from unittest import TestCase

import pytest

from xrlint.rule import Rule, define_rule
from xrlint.rule import RuleConfig
from xrlint.rule import RuleMeta
from xrlint.rule import RuleOp


class MyRule1(RuleOp):
    """This is my 1st rule."""


class MyRule2(RuleOp):
    """This is my 2nd rule."""


def export_rule():
    return Rule(meta=RuleMeta(name="my-rule-1"), op_class=MyRule1)


class RuleTest(TestCase):
    def test_from_value_ok_rule(self):
        rule = export_rule()
        rule2 = Rule.from_value(rule)
        self.assertIs(rule, rule2)

    def test_from_value_ok_rule_op(self):
        rule = export_rule()
        rule2 = Rule.from_value(rule)
        self.assertIs(rule, rule2)

    def test_from_value_ok_str(self):
        rule = Rule.from_value("tests.test_rule")
        self.assertIsInstance(rule, Rule)
        self.assertEqual("my-rule-1", rule.meta.name)
        self.assertIs(MyRule1, rule.op_class)

    # noinspection PyMethodMayBeStatic
    def test_from_value_fails(self):
        with pytest.raises(
            TypeError, match="value must be of type Rule|str, but got int"
        ):
            Rule.from_value(73)

        class MyRule3(RuleOp):
            """This is my 3rd rule."""

        with pytest.raises(
            ValueError,
            match="missing rule metadata, apply define_rule\\(\\) to class MyRule3",
        ):
            Rule.from_value(MyRule3)


class DefineRuleTest(unittest.TestCase):

    def test_decorator(self):
        deco = define_rule()
        self.assertTrue(callable(deco))
        op_class = deco(MyRule1)
        self.assertIs(MyRule1, op_class)
        self.assertTrue(hasattr(MyRule1, "meta"))
        # noinspection PyUnresolvedReferences
        self.assertEqual("my-rule-1", MyRule1.meta.name)

    def test_function(self):
        rule = define_rule(op_class=MyRule1)
        self.assertIsInstance(rule, Rule)
        self.assertEqual("my-rule-1", rule.meta.name)
        self.assertIs(MyRule1, rule.op_class)

    def test_with_registry(self):
        registry = {}
        rule1 = define_rule(op_class=MyRule1, registry=registry)
        rule2 = define_rule(op_class=MyRule2, registry=registry)
        self.assertIs(rule1, registry["my-rule-1"])
        self.assertIs(rule2, registry["my-rule-2"])


class RuleConfigTest(TestCase):
    def test_defaults(self):
        rule_config = RuleConfig(1)
        self.assertEqual(1, rule_config.severity)
        self.assertEqual((), rule_config.args)
        self.assertEqual({}, rule_config.kwargs)

    def test_from_value_ok(self):
        self.assertEqual(RuleConfig(0), RuleConfig.from_value(0))
        self.assertEqual(RuleConfig(1), RuleConfig.from_value(1))
        self.assertEqual(RuleConfig(2), RuleConfig.from_value(2))
        self.assertEqual(RuleConfig(0), RuleConfig.from_value("off"))
        self.assertEqual(RuleConfig(1), RuleConfig.from_value("warn"))
        self.assertEqual(RuleConfig(2), RuleConfig.from_value("error"))
        self.assertEqual(RuleConfig(2), RuleConfig.from_value(["error"]))
        self.assertEqual(
            RuleConfig(1, ("never",)), RuleConfig.from_value(["warn", "never"])
        )
        self.assertEqual(
            RuleConfig(1, ("always",)), RuleConfig.from_value([1, "always"])
        )
        self.assertEqual(
            RuleConfig(1, ("always", False)),
            RuleConfig.from_value([1, "always", False]),
        )
        self.assertEqual(
            RuleConfig(1, (), {"pattern": "*/*"}),
            RuleConfig.from_value([1, {"pattern": "*/*"}]),
        )
        self.assertEqual(
            RuleConfig(1, ("always",), {"pattern": "*/*"}),
            RuleConfig.from_value([1, "always", {"pattern": "*/*"}]),
        )
        self.assertEqual(
            RuleConfig(2, ("always", False), {"pattern": "*/*"}),
            RuleConfig.from_value([2, "always", False, {"pattern": "*/*"}]),
        )
        self.assertEqual(
            RuleConfig(0, ("always", {}), {"pattern": "*/*"}),
            RuleConfig.from_value(("off", "always", {}, {"pattern": "*/*"})),
        )

    # noinspection PyMethodMayBeStatic
    def test_from_value_fails(self):
        with pytest.raises(
            TypeError,
            match="rule configuration must be of type int|str|tuple|list, but got None",
        ):
            RuleConfig.from_value(None)
        with pytest.raises(
            ValueError,
            match="severity must be one of 'error', 'warn', 'off', 2, 1, 0, but got 4",
        ):
            RuleConfig.from_value(4)
        with pytest.raises(
            ValueError,
            match=(
                "severity must be one of 'error', 'warn', 'off',"
                " 2, 1, 0, but got 'debug'"
            ),
        ):
            RuleConfig.from_value("debug")
