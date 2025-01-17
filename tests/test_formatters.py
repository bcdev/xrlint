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
