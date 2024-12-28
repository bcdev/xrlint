from unittest import TestCase

from xrlint.plugins.core import plugin


class PluginTest(TestCase):
    def test_plugin(self):
        _plugin = plugin()
        self.assertEqual(
            {
                "dataset-title-attr",
                "no-empty-attrs",
                "var-units-attr",
            },
            set(_plugin.rules.keys()),
        )
