from unittest import TestCase

import pytest

from xrlint.rule import Rule
from xrlint.rule import RuleConfig
from xrlint.rule import RuleMeta
from xrlint.rule import RuleOp


class MyRule1Op(RuleOp):
    pass


def export_rule():
    return Rule(meta=RuleMeta(name="my-rule-1"), op_class=MyRule1Op)


class RuleTest(TestCase):
    def test_from_value_ok_rule(self):
        rule = export_rule()
        rule2 = Rule.from_value(rule)
        self.assertIs(rule, rule2)

    def test_from_value_ok_str(self):
        rule = Rule.from_value("tests.test_rule")
        self.assertIsInstance(rule, Rule)
        self.assertEqual("my-rule-1", rule.meta.name)
        self.assertIs(MyRule1Op, rule.op_class)

    # noinspection PyMethodMayBeStatic
    def test_from_value_fails(self):
        with pytest.raises(
            TypeError, match="value must be of type Rule|str, but was int"
        ):
            Rule.from_value(73)


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
            match="rule configuration must be of type int|str|tuple|list, but was None",
        ):
            RuleConfig.from_value(None)
        with pytest.raises(
            ValueError,
            match="severity must be one of 'error', 'warn', 'off', 2, 1, 0, but was 4",
        ):
            RuleConfig.from_value(4)
        with pytest.raises(
            ValueError,
            match=(
                "severity must be one of 'error', 'warn', 'off',"
                " 2, 1, 0, but was 'debug'"
            ),
        ):
            RuleConfig.from_value("debug")
