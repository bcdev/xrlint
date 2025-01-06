from typing import Any
from unittest import TestCase

import xarray as xr

from xrlint.plugin import Plugin, PluginMeta
from xrlint.processor import ProcessorOp, Processor
from xrlint.result import Message
from xrlint.rule import Rule, RuleOp


class PluginDefineRuleDecoratorTest(TestCase):

    # noinspection PyUnusedLocal
    def test_decorator(self):

        plugin = Plugin(meta=PluginMeta(name="test"))

        @plugin.define_rule("my-rule-1")
        class MyRule1(RuleOp):
            pass

        @plugin.define_rule("my-rule-2")
        class MyRule2(RuleOp):
            pass

        @plugin.define_rule("my-rule-3")
        class MyRule3(RuleOp):
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
        self.assertEqual("0.0.0", my_rule.meta.version)
        self.assertEqual(None, my_rule.meta.schema)
        self.assertEqual("problem", my_rule.meta.type)


class PluginDefineProcessorDecoratorTest(TestCase):

    # noinspection PyUnusedLocal
    def test_decorator(self):

        plugin = Plugin(meta=PluginMeta(name="test"))

        @plugin.define_processor("my-processor-1")
        class MyProcessor1(ProcessorOp):
            def preprocess(
                self, file_path: str, opener_options: dict[str, Any]
            ) -> list[tuple[xr.Dataset, str]]:
                return []

            def postprocess(
                self, messages: list[list[Message]], file_path: str
            ) -> list[Message]:
                return []

        @plugin.define_processor("my-processor-2")
        class MyProcessor2(ProcessorOp):
            def preprocess(
                self, file_path: str, opener_options: dict[str, Any]
            ) -> list[tuple[xr.Dataset, str]]:
                return []

            def postprocess(
                self, messages: list[list[Message]], file_path: str
            ) -> list[Message]:
                return []

        processors = plugin.processors
        processors_names = list(processors.keys())
        processor1, processor2 = list(processors.values())
        self.assertEqual(["my-processor-1", "my-processor-2"], processors_names)
        self.assertIsInstance(processor1, Processor)
        self.assertIsInstance(processor2, Processor)
        self.assertIsNot(processor1, processor2)

        my_processor = plugin.processors.get("my-processor-1")
        self.assertIsInstance(my_processor, Processor)
        self.assertEqual("my-processor-1", my_processor.meta.name)
        self.assertEqual("0.0.0", my_processor.meta.version)
