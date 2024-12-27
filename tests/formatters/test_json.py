from unittest import TestCase

import xrlint.api as xrl
from xrlint.config import Config
from xrlint.formatters.json import Json


class JsonTest(TestCase):
    def test_it(self):
        json_formatter = Json(2)
        text = json_formatter.format(
            context=xrl.FormatterContext(),
            results=[
                xrl.Result(
                    Config(),
                    file_path="test.nc",
                    messages=[
                        xrl.Message(message="what", severity=2),
                        xrl.Message(message="is", fatal=True),
                        xrl.Message(message="happening?", severity=1),
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
                '          "severity": 2\n'
                "        },\n"
                "        {\n"
                '          "message": "is",\n'
                '          "fatal": true\n'
                "        },\n"
                "        {\n"
                '          "message": "happening?",\n'
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
