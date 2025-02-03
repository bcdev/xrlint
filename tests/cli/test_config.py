#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

import unittest
from pathlib import Path
from typing import Any
from unittest import TestCase

import pytest

from xrlint.cli.config import ConfigError, read_config
from xrlint.config import Config, ConfigObject
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
def export_config():
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

    def test_read_config_py(self):
        with text_file(self.new_config_py(), py_text) as config_path:
            config = read_config(config_path)
            self.assert_config_ok(config, "py-test")

    def assert_config_ok(self, config: Any, name: str):
        self.assertEqual(
            Config(
                [
                    ConfigObject(
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
            match="configuration file must be of type str|Path|PathLike, but got None",
        ):
            # noinspection PyTypeChecker
            read_config(None)

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
                read_config(config_path)

    def test_read_config_yaml_with_format_error(self):
        with text_file("config.yaml", "}") as config_path:
            with pytest.raises(
                ConfigError,
                match="config.yaml: while parsing a block node",
            ):
                read_config(config_path)

    def test_read_config_yaml_with_type_error(self):
        with text_file("config.yaml", "97") as config_path:
            with pytest.raises(
                ConfigError,
                match=(
                    r"config\.yaml\: config must be of type"
                    r" Config \| ConfigObjectLike \| str \| Sequence\[ConfigObjectLike \| str\],"
                    r" but got int"
                ),
            ):
                read_config(config_path)

    def test_read_config_with_unknown_format(self):
        with pytest.raises(
            ConfigError,
            match="config.toml: unsupported configuration file format",
        ):
            read_config("config.toml")

    def test_read_config_py_no_export(self):
        py_code = "x = 42\n"
        with text_file(self.new_config_py(), py_code) as config_path:
            with pytest.raises(
                ConfigError,
                match=(
                    "config_1002.py: attribute 'export_config'"
                    " not found in module 'config_1002'"
                ),
            ):
                read_config(config_path)

    def test_read_config_py_with_value_error(self):
        py_code = "def export_config():\n    raise ValueError('value is useless!')\n"
        with text_file(self.new_config_py(), py_code) as config_path:
            with pytest.raises(
                ValueError,
                match="value is useless!",
            ):
                read_config(config_path)

    def test_read_config_py_with_os_error(self):
        py_code = "def export_config():\n    raise OSError('where is my hat?')\n"
        with text_file(self.new_config_py(), py_code) as config_path:
            with pytest.raises(
                ConfigError,
                match="where is my hat?",
            ):
                read_config(config_path)

    def test_read_config_py_with_invalid_config_list(self):
        py_code = "def export_config():\n    return 42\n"
        with text_file(self.new_config_py(), py_code) as config_path:
            with pytest.raises(
                ConfigError,
                match=(
                    r"\.py: failed converting value of 'config_1003:export_config':"
                    r" config must be of type"
                    r" Config \| ConfigObjectLike \| str \| Sequence\[ConfigObjectLike \| str\],"
                    r" but got int"
                ),
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

    def assert_ok(self, config: Config):
        self.assertIsInstance(config, Config)
        self.assertEqual(7, len(config.objects))
        config_obj = config.compute_config_object("test.zarr")
        self.assertIsInstance(config_obj, ConfigObject)
        self.assertEqual(None, config_obj.name)
        self.assertIsInstance(config_obj.plugins, dict)
        self.assertEqual({"xcube"}, set(config_obj.plugins.keys()))
        self.assertIsInstance(config_obj.rules, dict)
        self.assertIn("coords-for-dims", config_obj.rules)
        self.assertIn("xcube/cube-dims-order", config_obj.rules)
