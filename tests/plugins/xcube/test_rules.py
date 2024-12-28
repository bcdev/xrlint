from unittest import TestCase

from xrlint.plugins.xcube.rules import import_rules


class ImportRulesTest(TestCase):
    def test_import_rules(self):
        registry = import_rules()
        self.assertEqual(
            {
                "spatial-dims-order",
            },
            set(registry.as_dict().keys()),
        )
