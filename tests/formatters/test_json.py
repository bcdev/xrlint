from unittest import TestCase

from xrlint.formatter import FormatterContext
from xrlint.formatters.json import Json
from .helpers import get_test_results


class JsonTest(TestCase):
    def test_json(self):
        results = get_test_results()
        formatter = Json()
        text = formatter.format(
            context=FormatterContext(),
            results=results,
        )
        self.assertIn('"results": [', text)

    def test_json_with_meta(self):
        results = get_test_results()
        formatter = Json(with_meta=True)
        text = formatter.format(
            context=FormatterContext(),
            results=results,
        )
        self.assertIn('"results": [', text)
