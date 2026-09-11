#  Copyright © 2026 Brockmann Consult GmbH and contributors.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from unittest import TestCase

from xrlint.formatters import export_formatters


class ImportFormattersTest(TestCase):
    def test_import_formatters(self):
        registry = export_formatters()
        self.assertEqual(
            {
                "html",
                "json",
                "simple",
            },
            set(registry.keys()),
        )
