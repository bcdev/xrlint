from unittest import TestCase

from xrlint.config import Config
from xrlint.formatter import FormatterContext
from xrlint.formatters.json import Json
from xrlint.result import Message
from xrlint.result import Result


class JsonTest(TestCase):
    def test_json(self):
        formatter = Json(2)
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
        self.assertEqual(
            (
                "{\n"
                '  "results": [\n'
                "    {\n"
                '      "file_path": "test.nc",\n'
                '      "messages": [\n'
                "        {\n"
                '          "message": "what",\n'
                '          "rule_id": "rule-1",\n'
                '          "severity": 2\n'
                "        },\n"
                "        {\n"
                '          "message": "is",\n'
                '          "fatal": true\n'
                "        },\n"
                "        {\n"
                '          "message": "happening?",\n'
                '          "rule_id": "rule-2",\n'
                '          "severity": 1\n'
                "        }\n"
                "      ],\n"
                '      "fixable_error_count": 0,\n'
                '      "fixable_warning_count": 0,\n'
                '      "error_count": 0,\n'
                '      "fatal_error_count": 0,\n'
                '      "warning_count": 0\n'
                "    }\n"
                "  ]\n"
                "}"
            ),
            text,
        )
