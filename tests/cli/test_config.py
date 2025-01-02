import unittest
from pathlib import Path
from typing import Any
from unittest import TestCase

import click
import pytest

from xrlint.cli.config import read_config
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
            config = read_config(config_path)
            self.assert_config_ok(config, "yaml-test")

    def test_read_config_json(self):
        with text_file("config.json", json_text) as config_path:
            config = read_config(config_path)
            self.assert_config_ok(config, "json-test")

    def test_read_config_python(self):
        with text_file(self.new_config_py(), py_text) as config_path:
            config = read_config(config_path)
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

    def test_read_config_with_type_error(self):
        with pytest.raises(
            TypeError,
            match="configuration file must be of type str|Path|PathLike,"
            " but was None",
        ):
            # noinspection PyTypeChecker
            read_config(None)

    def test_read_config_with_format_error(self):
        with text_file("config.json", "{") as config_path:
            with pytest.raises(
                click.ClickException,
                match=(
                    "config.json:"
                    " Expecting property name enclosed in double quotes:"
                    " line 1 column 2 \\(char 1\\)"
                ),
            ):
                read_config(config_path)

    def test_read_config_with_unknown_format(self):
        with pytest.raises(
            click.ClickException,
            match="config.toml: unsupported configuration file format",
        ):
            read_config("config.toml")

    def test_read_config_python_no_export(self):
        py_code = "x = 42\n"
        with text_file(self.new_config_py(), py_code) as config_path:
            with pytest.raises(
                click.ClickException,
                match="has no attribute 'export_configs'",
            ):
                read_config(config_path)

    def test_read_config_with_exception(self):
        py_code = "def export_configs():\n    raise ValueError('no config here!')\n"
        with text_file(self.new_config_py(), py_code) as config_path:
            from xrlint.util.importutil import UserCodeException

            with pytest.raises(
                UserCodeException,
                match="while executing export_configs\\(\\): no config here!",
            ):
                read_config(config_path)


class CliConfigResolveTest(unittest.TestCase):
    def test_read_config_py(self):
        self.assert_ok(
            read_config(Path(__file__).parent / "configs" / "recommended.py")
        )

    def test_read_config_json(self):
        self.assert_ok(
            read_config(Path(__file__).parent / "configs" / "recommended.json")
        )

    def test_read_config_yaml(self):
        self.assert_ok(
            read_config(Path(__file__).parent / "configs" / "recommended.yaml")
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
