from unittest import TestCase

from xrlint.formatter import Formatter
from xrlint.formatter import FormatterOp
from xrlint.formatter_reg import FormatterRegistry


class DefineFormatterDecoratorTest(TestCase):
    def test_default_meta(self):

        registry = FormatterRegistry()

        @registry.define_formatter()
        class MyFormat(FormatterOp):
            def format(self, *args, **kwargs) -> str:
                """Dummy"""

        my_rule = registry.get("my-format")
        self.assertIsInstance(my_rule, Formatter)
        self.assertEqual("my-format", my_rule.meta.name)
        self.assertEqual(None, my_rule.meta.version)
        self.assertEqual(None, my_rule.meta.schema)

    def test_multi_registration(self):

        registry = FormatterRegistry()

        @registry.define_formatter(name="my-fmt-a")
        class MyFormat1(FormatterOp):
            def format(self, *args, **kwargs) -> str:
                """Dummy"""

        @registry.define_formatter(name="my-fmt-b")
        class MyFormat2(FormatterOp):
            def format(self, *args, **kwargs) -> str:
                """Dummy"""

        @registry.define_formatter(name="my-fmt-c")
        class MyFormat3(FormatterOp):
            def format(self, *args, **kwargs) -> str:
                """Dummy"""

        d = registry.as_dict()
        fmt_names = list(d.keys())
        fmt1, fmt2, fmt3 = list(d.values())
        self.assertEqual(["my-fmt-a", "my-fmt-b", "my-fmt-c"], fmt_names)
        self.assertIsInstance(fmt1, Formatter)
        self.assertIsInstance(fmt2, Formatter)
        self.assertIsInstance(fmt3, Formatter)
        self.assertIsNot(fmt2, fmt1)
        self.assertIsNot(fmt3, fmt1)
        self.assertIsNot(fmt3, fmt2)
