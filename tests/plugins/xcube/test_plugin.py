from unittest import TestCase

from xrlint.plugins.xcube import export_plugin


class ExportPluginTest(TestCase):

    def test_configs_complete(self):
        _plugin = export_plugin()
        self.assertEqual(
            {
                "all",
                "recommended",
            },
            set(_plugin.configs.keys()),
        )

    def test_rules_complete(self):
        _plugin = export_plugin()
        self.assertEqual(
            {
                "any-spatial-data-var",
                "cube-dims-order",
                "data-var-colors",
                "grid-mapping-naming",
                "lat-lon-naming",
                "single-grid-mapping",
                "increasing-time",
            },
            set(_plugin.rules.keys()),
        )
