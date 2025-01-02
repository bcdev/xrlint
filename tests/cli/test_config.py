import unittest
from pathlib import Path
from typing import Any
from unittest import TestCase

import click
import fsspec
import pytest

from xrlint.cli.config import read_config
from xrlint.cli.constants import DEFAULT_CONFIG_BASENAME
from xrlint.cli.constants import DEFAULT_CONFIG_FILE_YAML
from xrlint.cli.constants import DEFAULT_CONFIG_FILE_JSON
from xrlint.cli.constants import DEFAULT_CONFIG_FILE_PY
from xrlint.config import Config
from xrlint.config import ConfigList
from xrlint.rule import RuleConfig

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
    def test_read_config_yaml(self):
        config_path = f"memory://{DEFAULT_CONFIG_FILE_YAML}"
        with fsspec.open(config_path, mode="w") as f:
            f.write(yaml_text)

        config = read_config(config_path)
        self.assert_config_ok(config, "yaml-test")

    def test_read_config_json(self):
        config_path = f"memory://{DEFAULT_CONFIG_FILE_JSON}"
        with fsspec.open(config_path, mode="w") as f:
            f.write(json_text)

        config = read_config(config_path)
        self.assert_config_ok(config, "json-test")

    def test_read_config_python(self):
        config_path = f"memory://{DEFAULT_CONFIG_FILE_PY}"
        with fsspec.open(config_path, mode="w") as f:
            f.write(py_text)

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
        config_path = f"memory://{DEFAULT_CONFIG_FILE_JSON}"
        with fsspec.open(config_path, mode="w") as f:
            f.write("{")

        with pytest.raises(
            click.ClickException,
            match=(
                "memory://xrlint.config.json:"
                " Expecting property name enclosed in double quotes:"
                " line 1 column 2 \\(char 1\\)"
            ),
        ):
            read_config(config_path)

    def test_read_config_with_unknown_format(self):
        config_path = f"memory://{DEFAULT_CONFIG_BASENAME}.toml"
        with fsspec.open(config_path, mode="w") as f:
            f.write("")

        with pytest.raises(
            click.ClickException,
            match="memory://xrlint.config.toml: unsupported configuration file format",
        ):
            read_config(config_path)

    def test_read_config_python_no_export(self):
        config_path = f"memory://{DEFAULT_CONFIG_BASENAME}.py"
        with fsspec.open(config_path, mode="w") as f:
            f.write("")

        with pytest.raises(
            click.ClickException,
            match=(
                "memory://xrlint_config.py: missing definition"
                " of function 'export_configs'"
            ),
        ):
            read_config(config_path)

    def test_read_config_with_exception(self):
        config_path = f"memory://{DEFAULT_CONFIG_BASENAME}.py"
        with fsspec.open(config_path, mode="w") as f:
            f.write("def export_configs():\n    raise ValueError('no config here!')\n")

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
