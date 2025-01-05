from unittest import TestCase

from xrlint.config import Config
from xrlint.formatter import FormatterContext
from xrlint.formatters.simple import Simple
from xrlint.result import Message
from xrlint.result import Result


class SimpleTest(TestCase):
    def test_simple(self):
        formatter = Simple()
        text = formatter.format(
            context=FormatterContext(),
            results=[
                Result.new(
                    Config(),
                    file_path="test.nc",
                    messages=[
                        Message(message="what", rule_id="rule-1", severity=2),
                        Message(message="is", fatal=True),
                        Message(message="happening?", rule_id="rule-2", severity=1),
                    ],
                )
            ],
        )
        self.assertIsInstance(text, str)
        self.assertIn("test.nc:\n", text)
        self.assertIn("happening?", text)
        self.assertIn("error", text)
        self.assertIn("warn", text)
        self.assertIn("rule-1", text)
        self.assertIn("rule-2", text)
