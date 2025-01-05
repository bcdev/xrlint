from unittest import TestCase

import pytest

from xrlint.config import Config
from xrlint.formatter import FormatterContext
from xrlint.formatters.markdown import Markdown
from xrlint.result import Message
from xrlint.result import Result


class MarkdownTest(TestCase):
    def test_markdown(self):
        formatter = Markdown()
        with pytest.raises(NotImplementedError):
            formatter.format(
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
