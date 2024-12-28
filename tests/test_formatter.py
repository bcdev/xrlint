from unittest import TestCase

from xrlint.formatter import Formatter
from xrlint.formatter import FormatterOp
from xrlint.formatter import FormatterRegistry


class FormatterRegistryTest(TestCase):
    def test_decorator_sets_meta(self):

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

    def test_decorator_registrations(self):

        registry = FormatterRegistry()

        @registry.define_formatter("my-fmt-a")
        class MyFormat1(FormatterOp):
            def format(self, *args, **kwargs) -> str:
                """Dummy"""

        @registry.define_formatter("my-fmt-b")
        class MyFormat2(FormatterOp):
            def format(self, *args, **kwargs) -> str:
                """Dummy"""

        @registry.define_formatter("my-fmt-c")
        class MyFormat3(FormatterOp):
            def format(self, *args, **kwargs) -> str:
                """Dummy"""

        fmt_names = list(registry.keys())
        fmt1, fmt2, fmt3 = list(registry.values())
        self.assertEqual(["my-fmt-a", "my-fmt-b", "my-fmt-c"], fmt_names)
        self.assertIsInstance(fmt1, Formatter)
        self.assertIsInstance(fmt2, Formatter)
        self.assertIsInstance(fmt3, Formatter)
        self.assertIsNot(fmt2, fmt1)
        self.assertIsNot(fmt3, fmt1)
        self.assertIsNot(fmt3, fmt2)
