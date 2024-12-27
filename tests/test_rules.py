from unittest import TestCase

from xrlint.rules import import_rules


class ImportRulesTest(TestCase):
    def test_import_rules(self):
        registry = import_rules()
        self.assertEqual(
            {
                "dataset-title-attr",
                "no-empty-attrs",
                "var-units-attr",
            },
            set(registry.as_dict().keys()),
        )
