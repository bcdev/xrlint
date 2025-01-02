import unittest
from pathlib import Path
from typing import Any
from unittest import TestCase

import pytest

from xrlint.cli.config import ConfigError
from xrlint.cli.config import read_config_list
from xrlint.config import Config
from xrlint.config import ConfigList
from xrlint.rule import RuleConfig
from .helpers import text_file

yaml_text = """
- name: yaml-test
  rules:
    rule-1: 2
    rule-2: "warn"
    rule-3: ["error", {max_size: 500}]
"""


json_text = """
[
    {
        "name": "json-test",
        "rules": {
          "rule-1": 2,
          "rule-2": "warn",
          "rule-3": ["error", {"max_size": 500}]
        }
    }
]
"""

py_text = """
def export_configs():
    return [
        {
            "name": "py-test",
            "rules": {
                "rule-1": 2,
                "rule-2": 1,
                "rule-3": [2, {"max_size": 500}]
            }
        }
    ]
"""


# noinspection PyMethodMayBeStatic
class CliConfigTest(TestCase):
    module_no = 1000

    def new_config_py(self):
        CliConfigTest.module_no += 1
        return f"config_{CliConfigTest.module_no}.py"

    def test_read_config_yaml(self):
        with text_file("config.yaml", yaml_text) as config_path:
            config = read_config_list(config_path)
            self.assert_config_ok(config, "yaml-test")

    def test_read_config_json(self):
        with text_file("config.json", json_text) as config_path:
            config = read_config_list(config_path)
            self.assert_config_ok(config, "json-test")

    def test_read_config_py(self):
        with text_file(self.new_config_py(), py_text) as config_path:
            config = read_config_list(config_path)
            self.assert_config_ok(config, "py-test")

    def assert_config_ok(self, config: Any, name: str):
        self.assertEqual(
            ConfigList(
                [
                    Config(
                        name=name,
                        rules={
                            "rule-1": RuleConfig(2),
                            "rule-2": RuleConfig(1),
                            "rule-3": RuleConfig(2, kwargs={"max_size": 500}),
                        },
                    )
                ]
            ),
            config,
        )

    def test_read_config_invalid_arg(self):
        with pytest.raises(
            TypeError,
            match="configuration file must be of type str|Path|PathLike,"
            " but was None",
        ):
            # noinspection PyTypeChecker
            read_config_list(None)

    def test_read_config_json_with_format_error(self):
        with text_file("config.json", "{") as config_path:
            with pytest.raises(
                ConfigError,
                match=(
                    "config.json:"
                    " Expecting property name enclosed in double quotes:"
                    " line 1 column 2 \\(char 1\\)"
                ),
            ):
                read_config_list(config_path)

    def test_read_config_yaml_with_format_error(self):
        with text_file("config.yaml", "}") as config_path:
            with pytest.raises(
                ConfigError,
                match="config.yaml: while parsing a block node",
            ):
                read_config_list(config_path)

    def test_read_config_yaml_with_type_error(self):
        with text_file("config.yaml", "prime: 97") as config_path:
            with pytest.raises(
                ConfigError,
                match=(
                    "'config.yaml: configuration list must be of"
                    " type ConfigList|list\\[Config|dict|str\\],"
                    " but was dict'"
                ),
            ):
                read_config_list(config_path)

    def test_read_config_with_unknown_format(self):
        with pytest.raises(
            ConfigError,
            match="config.toml: unsupported configuration file format",
        ):
            read_config_list("config.toml")

    def test_read_config_py_no_export(self):
        py_code = "x = 42\n"
        with text_file(self.new_config_py(), py_code) as config_path:
            with pytest.raises(
                ConfigError,
                match=".py: missing export_configs()",
            ):
                read_config_list(config_path)

    def test_read_config_py_with_value_error(self):
        py_code = "def export_configs():\n    raise ValueError('value is useless!')\n"
        with text_file(self.new_config_py(), py_code) as config_path:
            with pytest.raises(
                ValueError,
                match="value is useless!",
            ):
                read_config_list(config_path)

    def test_read_config_py_with_os_error(self):
        py_code = "def export_configs():\n    raise OSError('where is my hat?')\n"
        with text_file(self.new_config_py(), py_code) as config_path:
            with pytest.raises(
                ConfigError,
                match="where is my hat?",
            ):
                read_config_list(config_path)

    def test_read_config_py_with_invalid_config_list(self):
        py_code = "def export_configs():\n    return 42\n"
        with text_file(self.new_config_py(), py_code) as config_path:
            with pytest.raises(
                ConfigError,
                match=(
                    ".py: return value of export_configs\\(\\):"
                    " configuration list must be of type"
                    " ConfigList|list\\[Config|dict|str\\],"
                    " but was int"
                ),
            ):
                read_config_list(config_path)


class CliConfigResolveTest(unittest.TestCase):
    def test_read_config_py(self):
        self.assert_ok(
            read_config_list(Path(__file__).parent / "configs" / "recommended.py")
        )

    def test_read_config_json(self):
        self.assert_ok(
            read_config_list(Path(__file__).parent / "configs" / "recommended.json")
        )

    def test_read_config_yaml(self):
        self.assert_ok(
            read_config_list(Path(__file__).parent / "configs" / "recommended.yaml")
        )

    def assert_ok(self, config_list: ConfigList):
        self.assertIsInstance(config_list, ConfigList)
        self.assertEqual(4, len(config_list.configs))
        config = config_list.compute_config("test.zarr")
        self.assertIsInstance(config, Config)
        self.assertEqual("<computed>", config.name)
        self.assertIsInstance(config.plugins, dict)
        self.assertEqual({"xcube"}, set(config.plugins.keys()))
        self.assertIsInstance(config.rules, dict)
        self.assertIn("coords-for-dims", config.rules)
        self.assertIn("xcube/cube-dims-order", config.rules)
