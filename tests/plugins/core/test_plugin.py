from unittest import TestCase

from xrlint.plugins.core import export_plugin


class PluginTest(TestCase):
    def test_plugin(self):
        _plugin = export_plugin()
        self.assertEqual(
            {
                "dataset-title-attr",
                "no-empty-attrs",
                "var-units-attr",
            },
            set(_plugin.rules.keys()),
        )
