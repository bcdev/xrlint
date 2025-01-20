from unittest import TestCase

from xrlint.plugins.core import export_plugin


class ExportPluginTest(TestCase):
    def test_rules_complete(self):
        plugin = export_plugin()
        self.assertEqual(
            {
                "coords-for-dims",
                "dataset-title-attr",
                "flags",
                "grid-mappings",
                "lat-coordinate",
                "lon-coordinate",
                "no-empty-attrs",
                "time-coordinate",
                "var-units-attr",
            },
            set(plugin.rules.keys()),
        )

    def test_configs_complete(self):
        plugin = export_plugin()
        self.assertEqual(
            {
                "all",
                "recommended",
            },
            set(plugin.configs.keys()),
        )
        all_rule_names = set(plugin.rules.keys())
        self.assertEqual(
            all_rule_names,
            set(plugin.configs["all"].rules.keys()),
        )
        self.assertEqual(
            all_rule_names,
            set(plugin.configs["recommended"].rules.keys()),
        )
