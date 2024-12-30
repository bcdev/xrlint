from unittest import TestCase

import pytest

from xrlint.rule import RuleConfig
from xrlint.config import Config


# noinspection PyMethodMayBeStatic
class ConfigTest(TestCase):
    def test_defaults(self):
        config = Config()
        self.assertEqual(None, config.name)
        self.assertEqual(None, config.files)
        self.assertEqual(None, config.ignores)
        self.assertEqual(None, config.linter_options)
        self.assertEqual(None, config.opener_options)
        self.assertEqual(None, config.processor)
        self.assertEqual(None, config.plugins)
        self.assertEqual(None, config.rules)

    def test_from_value_ok(self):
        self.assertEqual(Config(), Config.from_value(None))
        self.assertEqual(Config(), Config.from_value({}))
        self.assertEqual(Config(), Config.from_value(Config()))
        self.assertEqual(Config(name="x"), Config.from_value(Config(name="x")))

    def test_from_value_fails(self):
        with pytest.raises(
            TypeError, match="configuration must be of type dict, but was int"
        ):
            Config.from_value(4)
        with pytest.raises(
            TypeError, match="configuration must be of type dict, but was str"
        ):
            Config.from_value("abc")
        with pytest.raises(
            TypeError, match="configuration must be of type dict, but was tuple"
        ):
            Config.from_value(())

    def test_global_ignores(self):
        ignores = ["*.tiff", "*.txt"]
        self.assertEqual(ignores, Config(ignores=ignores).global_ignores)
        self.assertEqual(ignores, Config(ignores=ignores, name="Empty?").global_ignores)
        self.assertEqual(ignores, Config(ignores=ignores, rules={}).global_ignores)
        self.assertEqual(ignores, Config(ignores=ignores, settings={}).global_ignores)
        self.assertEqual(ignores, Config(ignores=ignores, files=[]).global_ignores)
        self.assertEqual([], Config(rules={"x": RuleConfig(0)}).global_ignores)
        self.assertEqual([], Config(settings={"a": 17}).global_ignores)
        self.assertEqual([], Config(ignores=ignores, settings={"a": 17}).global_ignores)
        self.assertEqual(
            [], Config(ignores=ignores, rules={"x": RuleConfig(0)}).global_ignores
        )
