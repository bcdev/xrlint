from unittest import TestCase

from xrlint.plugins.xcube import plugin


class PluginTest(TestCase):
    def test_plugin(self):
        _plugin = plugin()
        self.assertEqual(
            {
                "spatial-dims-order",
            },
            set(_plugin.rules.keys()),
        )
