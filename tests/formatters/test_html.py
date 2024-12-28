from unittest import TestCase

from xrlint.config import Config
from xrlint.formatter import FormatterContext
from xrlint.formatters.html import Html
from xrlint.result import Message
from xrlint.result import Result


class HtmlTest(TestCase):
    def test_html(self):
        formatter = Html()
        text = formatter.format(
            context=FormatterContext(),
            results=[
                Result(
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
        self.assertIn("</p>", text)
