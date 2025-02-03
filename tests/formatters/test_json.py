#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from unittest import TestCase

from xrlint.formatters.json import Json

from .helpers import get_context, get_test_results


class JsonTest(TestCase):
    def test_json(self):
        results = get_test_results()
        formatter = Json()
        text = formatter.format(
            context=get_context(),
            results=results,
        )
        self.assertIn('"results": [', text)

    def test_json_with_meta(self):
        results = get_test_results()
        formatter = Json(with_meta=True)
        text = formatter.format(
            context=get_context(),
            results=results,
        )
        self.assertIn('"results": [', text)
