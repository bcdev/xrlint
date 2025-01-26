from unittest import TestCase

from tests.formatters.helpers import get_context
from xrlint.config import Config
from xrlint.formatters.simple import Simple
from xrlint.result import Message, Result


class SimpleTest(TestCase):
    errors_and_warnings = [
        Result.new(
            Config(),
            file_path="test1.nc",
            messages=[
                Message(message="what", rule_id="rule-1", severity=2),
                Message(message="is", fatal=True),
                Message(message="happening?", rule_id="rule-2", severity=1),
            ],
        )
    ]

    warnings_only = [
        Result.new(
            Config(),
            file_path="test2.nc",
            messages=[
                Message(message="what", rule_id="rule-1", severity=1),
                Message(message="happened?", rule_id="rule-2", severity=1),
            ],
        )
    ]

    def test_no_color(self):
        formatter = Simple(styled=False)
        text = formatter.format(
            context=get_context(),
            results=self.errors_and_warnings,
        )
        self.assert_output_1_ok(text)
        self.assertNotIn("\033]", text)

        formatter = Simple(styled=False)
        text = formatter.format(
            context=get_context(),
            results=self.warnings_only,
        )
        self.assert_output_2_ok(text)
        self.assertNotIn("\033]", text)

    def test_color(self):
        formatter = Simple(styled=True)
        text = formatter.format(
            context=get_context(),
            results=self.errors_and_warnings,
        )
        self.assert_output_1_ok(text)
        self.assertIn("\033]", text)

        formatter = Simple(styled=True)
        text = formatter.format(
            context=get_context(),
            results=self.warnings_only,
        )
        self.assert_output_2_ok(text)
        self.assertIn("\033]", text)

    def assert_output_1_ok(self, text):
        self.assertIsInstance(text, str)
        self.assertIn("test1.nc", text)
        self.assertIn("happening?", text)
        self.assertIn("error", text)
        self.assertIn("warn", text)
        self.assertIn("rule-1", text)
        self.assertIn("rule-2", text)

    def assert_output_2_ok(self, text):
        self.assertIsInstance(text, str)
        self.assertIn("test2.nc", text)
        self.assertIn("happened?", text)
        self.assertNotIn("error", text)
        self.assertIn("warn", text)
        self.assertIn("rule-1", text)
        self.assertIn("rule-2", text)
