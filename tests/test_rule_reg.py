from unittest import TestCase

from xrlint.rule_reg import RuleRegistry
from xrlint.rule import Rule, RuleOp


class DefineRuleDecoratorTest(TestCase):
    def test_default_meta(self):

        registry = RuleRegistry()

        @registry.define_rule()
        class MyRule(RuleOp):
            pass

        my_rule = registry.get("my-rule")
        self.assertIsInstance(my_rule, Rule)
        self.assertEqual("my-rule", my_rule.meta.name)
        self.assertEqual(None, my_rule.meta.version)
        self.assertEqual(None, my_rule.meta.schema)
        self.assertEqual("problem", my_rule.meta.type)

    def test_multi_registration(self):

        registry = RuleRegistry()

        @registry.define_rule(name="my-rule-1")
        class MyRule1(RuleOp):
            pass

        @registry.define_rule(name="my-rule-2")
        class MyRule2(RuleOp):
            pass

        @registry.define_rule(name="my-rule-3")
        class MyRule2(RuleOp):
            pass

        d = registry.as_dict()
        rule_names = list(d.keys())
        rule1, rule2, rule3 = list(d.values())
        self.assertEqual(["my-rule-1", "my-rule-2", "my-rule-3"], rule_names)
        self.assertIsInstance(rule1, Rule)
        self.assertIsInstance(rule2, Rule)
        self.assertIsInstance(rule3, Rule)
        self.assertIsNot(rule2, rule1)
        self.assertIsNot(rule3, rule1)
        self.assertIsNot(rule3, rule2)
