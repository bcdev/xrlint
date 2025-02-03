#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from unittest import TestCase

from xrlint.formatters.html import Html, HtmlText

from .helpers import get_context, get_test_results


class HtmlTest(TestCase):
    def test_html(self):
        results = get_test_results()
        formatter = Html()
        text = formatter.format(
            context=get_context(),
            results=results,
        )
        self.assertIsInstance(text, HtmlText)
        self.assertIs(text, text._repr_html_())
        self.assertIn("</p>", text)

    def test_html_with_meta(self):
        results = get_test_results()
        formatter = Html(with_meta=True)
        text = formatter.format(
            context=get_context(),
            results=results,
        )
        self.assertIsInstance(text, HtmlText)
        self.assertIs(text, text._repr_html_())
        self.assertIn("</p>", text)
