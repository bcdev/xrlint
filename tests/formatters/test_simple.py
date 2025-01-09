from unittest import TestCase

from tests.formatters.helpers import get_context
from xrlint.config import Config
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
        formatter = Simple(styled=False)
        text = formatter.format(
            context=get_context(),
            results=self.results,
        )
        self.assert_output_ok(text)
        self.assertNotIn("\033]", text)

    def test_color(self):
        formatter = Simple(styled=True)
        text = formatter.format(
            context=get_context(),
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
