from unittest import TestCase

from xrlint.formatters import import_formatters


class ImportFormattersTest(TestCase):
    def test_import_formatters(self):
        registry = import_formatters()
        self.assertEqual(
            {
                "html",
                "json",
                "markdown",
                "simple",
            },
            set(registry.as_dict().keys()),
        )
