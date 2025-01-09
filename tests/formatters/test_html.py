from unittest import TestCase

from xrlint.formatters.html import Html
from .helpers import get_test_results, get_context


class HtmlTest(TestCase):
    def test_html(self):
        results = get_test_results()
        formatter = Html()
        text = formatter.format(
            context=get_context(),
            results=results,
        )
        self.assertIsInstance(text, str)
        self.assertIn("</p>", text)

    def test_html_with_meta(self):
        results = get_test_results()
        formatter = Html(with_meta=True)
        text = formatter.format(
            context=get_context(),
            results=results,
        )
        self.assertIsInstance(text, str)
        self.assertIn("</p>", text)
