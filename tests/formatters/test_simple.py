from unittest import TestCase

from xrlint.config import Config
from xrlint.formatter import FormatterContext
from xrlint.formatters.simple import Simple
from xrlint.result import Message
from xrlint.result import Result


class SimpleTest(TestCase):
    results = [
        Result.new(
            Config(),
            file_path="test.nc",
            messages=[
                Message(message="what", rule_id="rule-1", severity=2),
                Message(message="is", fatal=True),
                Message(message="happening?", rule_id="rule-2", severity=1),
            ],
        )
    ]

    def test_no_color(self):
        formatter = Simple(color_enabled=False)
        text = formatter.format(
            context=FormatterContext(),
            results=self.results,
        )
        self.assert_output_ok(text)
        self.assertNotIn("\033]", text)

    def test_color(self):
        formatter = Simple(color_enabled=True)
        text = formatter.format(
            context=FormatterContext(),
            results=self.results,
        )
        self.assert_output_ok(text)
        self.assertIn("\033]", text)

    def assert_output_ok(self, text):
        self.assertIsInstance(text, str)
        self.assertIn("test.nc", text)
        self.assertIn("happening?", text)
        self.assertIn("error", text)
        self.assertIn("warn", text)
        self.assertIn("rule-1", text)
        self.assertIn("rule-2", text)
