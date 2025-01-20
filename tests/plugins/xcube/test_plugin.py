from unittest import TestCase

from xrlint.plugins.xcube import export_plugin


class ExportPluginTest(TestCase):
    def test_rules_complete(self):
        plugin = export_plugin()
        self.assertEqual(
            {
                "any-spatial-data-var",
                "cube-dims-order",
                "data-var-colors",
                "grid-mapping-naming",
                "increasing-time",
                "lat-lon-naming",
                "single-grid-mapping",
                "time-naming",
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
        all_rule_names = set(f"xcube/{k}" for k in plugin.rules.keys())
        self.assertEqual(
            all_rule_names,
            set(plugin.configs["all"].rules.keys()),
        )
        self.assertEqual(
            all_rule_names,
            set(plugin.configs["recommended"].rules.keys()),
        )
