#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

import unittest
from unittest import TestCase

from xrlint.config import Config
from xrlint.rule import RuleOp
from xrlint.util.importutil import import_value


class ExamplesTest(TestCase):
    def test_plugin_config(self):
        config, _ = import_value(
            "examples.plugin_config", "export_config", factory=Config.from_value
        )
        self.assertIsInstance(config, Config)
        self.assertEqual(3, len(config.objects))

    def test_virtual_plugin_config(self):
        config, _ = import_value(
            "examples.virtual_plugin_config",
            "export_config",
            factory=Config.from_value,
        )
        self.assertIsInstance(config, Config)
        self.assertEqual(3, len(config.objects))

    def test_rule_testing(self):
        from examples.rule_testing import GoodTitle, GoodTitleTest

        self.assertTrue(issubclass(GoodTitle, RuleOp))
        self.assertTrue(issubclass(GoodTitleTest, unittest.TestCase))
