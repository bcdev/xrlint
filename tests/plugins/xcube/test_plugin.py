from unittest import TestCase

from xrlint.plugins.xcube import export_plugin


class ExportPluginTest(TestCase):

    def test_configs_complete(self):
        _plugin = export_plugin()
        self.assertEqual(
            {
                "recommended",
            },
            set(_plugin.configs.keys()),
        )

    def test_rules_complete(self):
        _plugin = export_plugin()
        self.assertEqual(
            {
                "spatial-dims-order",
            },
            set(_plugin.rules.keys()),
        )
