from unittest import TestCase

from xrlint.formatters import export_formats


class ImportFormattersTest(TestCase):
    def test_import_formatters(self):
        registry = export_formats()
        self.assertEqual(
            {
                "html",
                "json",
                "markdown",
                "simple",
            },
            set(registry.keys()),
        )
