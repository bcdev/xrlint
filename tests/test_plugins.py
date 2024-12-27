from unittest import TestCase

from xrlint.plugin import Plugin


class PluginsTest(TestCase):
    def test_xcube(self):
        plugin = Plugin.from_value("xrlint.plugins.xcube")
        self.assertIsInstance(plugin, Plugin)
