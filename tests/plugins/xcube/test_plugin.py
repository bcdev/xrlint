from unittest import TestCase

from xrlint.plugins.xcube import export_plugin


class PluginTest(TestCase):
    def test_plugin(self):
        _plugin = export_plugin()
        self.assertEqual(
            {
                "spatial-dims-order",
            },
            set(_plugin.rules.keys()),
        )
