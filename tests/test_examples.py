import unittest
from unittest import TestCase

from xrlint.config import ConfigList
from xrlint.rule import RuleOp
from xrlint.util.importutil import import_value


class ExamplesTest(TestCase):
    def test_plugin_config(self):
        config_list, _ = import_value(
            "examples.plugin_config", "export_configs", factory=ConfigList.from_value
        )
        self.assertIsInstance(config_list, ConfigList)
        self.assertEqual(3, len(config_list.configs))

    def test_virtual_plugin_config(self):
        config_list, _ = import_value(
            "examples.virtual_plugin_config",
            "export_configs",
            factory=ConfigList.from_value,
        )
        self.assertIsInstance(config_list, ConfigList)
        self.assertEqual(3, len(config_list.configs))

    def test_rule_testing(self):
        from examples.rule_testing import GoodTitle, GoodTitleTest

        self.assertTrue(issubclass(GoodTitle, RuleOp))
        self.assertTrue(issubclass(GoodTitleTest, unittest.TestCase))
