from unittest import TestCase

from xrlint.plugin import Plugin, PluginMeta
from xrlint.rule import Rule, RuleOp


class PluginDefineRuleDecoratorTest(TestCase):

    def test_decorator(self):

        plugin = Plugin(meta=PluginMeta(name="test"))

        @plugin.define_rule("my-rule-1")
        class MyRule1(RuleOp):
            pass

        @plugin.define_rule("my-rule-2")
        class MyRule2(RuleOp):
            pass

        @plugin.define_rule("my-rule-3")
        class MyRule2(RuleOp):
            pass

        rules = plugin.rules
        rule_names = list(rules.keys())
        rule1, rule2, rule3 = list(rules.values())
        self.assertEqual(["my-rule-1", "my-rule-2", "my-rule-3"], rule_names)
        self.assertIsInstance(rule1, Rule)
        self.assertIsInstance(rule2, Rule)
        self.assertIsInstance(rule3, Rule)
        self.assertIsNot(rule2, rule1)
        self.assertIsNot(rule3, rule1)
        self.assertIsNot(rule3, rule2)

        my_rule = plugin.rules.get("my-rule-1")
        self.assertIsInstance(my_rule, Rule)
        self.assertEqual("my-rule-1", my_rule.meta.name)
        self.assertEqual(None, my_rule.meta.version)
        self.assertEqual(None, my_rule.meta.schema)
        self.assertEqual("problem", my_rule.meta.type)
