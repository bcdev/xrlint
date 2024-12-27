from unittest import TestCase

import pytest

from xrlint.rule import RuleConfig
from xrlint.config import Config


# noinspection PyMethodMayBeStatic
class ConfigObjTest(TestCase):
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

    def test_empty_true(self):
        self.assertEqual(True, Config().empty)
        self.assertEqual(True, Config(name="Empty?").empty)
        self.assertEqual(True, Config(rules={}).empty)
        self.assertEqual(True, Config(settings={}).empty)
        self.assertEqual(True, Config(files=[]).empty)
        self.assertEqual(True, Config(ignores=[]).empty)

    def test_empty_false(self):
        self.assertEqual(False, Config(rules={"x": RuleConfig(0)}).empty)
        self.assertEqual(False, Config(settings={"a": 17}).empty)
