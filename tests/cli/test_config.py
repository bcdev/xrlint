from typing import Any
from unittest import TestCase

import click
import fsspec
import pytest

from xrlint.cli.config import read_config
from xrlint.cli.constants import CONFIG_DEFAULT_BASENAME
from xrlint.config import Config
from xrlint.config import ConfigList
from xrlint.rule import RuleConfig

yaml_text = """
- name: yaml-test
  plugins:
    
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
    def test_read_config_yaml(self):
        config_path = f"memory://{CONFIG_DEFAULT_BASENAME}.yaml"
        with fsspec.open(config_path, mode="w") as f:
            f.write(yaml_text)

        config = read_config(config_path)
        self.assert_config_ok(config, "yaml-test")

    def test_read_config_json(self):
        config_path = f"memory://{CONFIG_DEFAULT_BASENAME}.json"
        with fsspec.open(config_path, mode="w") as f:
            f.write(json_text)

        config = read_config(config_path)
        self.assert_config_ok(config, "json-test")

    def test_read_config_python(self):
        config_path = f"memory://{CONFIG_DEFAULT_BASENAME}.py"
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
        config_path = f"memory://{CONFIG_DEFAULT_BASENAME}.json"
        with fsspec.open(config_path, mode="w") as f:
            f.write("{")

        with pytest.raises(
            click.ClickException,
            match="memory://xrlint.config.json: Expecting property name enclosed in double quotes:"
            " line 1 column 2 \\(char 1\\)",
        ):
            read_config(config_path)

    def test_read_config_with_unknown_format(self):
        config_path = f"memory://{CONFIG_DEFAULT_BASENAME}.toml"
        with fsspec.open(config_path, mode="w") as f:
            f.write("")

        with pytest.raises(
            click.ClickException,
            match="memory://xrlint.config.toml: unsupported configuration file format",
        ):
            read_config(config_path)

    def test_read_config_python_no_export(self):
        config_path = f"memory://{CONFIG_DEFAULT_BASENAME}.py"
        with fsspec.open(config_path, mode="w") as f:
            f.write("")

        with pytest.raises(
            click.ClickException,
            match="memory://xrlint.config.py: missing definition of function 'export_config'",
        ):
            read_config(config_path)

    def test_read_config_with_exception(self):
        config_path = f"memory://{CONFIG_DEFAULT_BASENAME}.py"
        with fsspec.open(config_path, mode="w") as f:
            f.write("def export_config():\n    raise ValueError('no config here!')\n")

        from xrlint.util.importutil import UserCodeException

        with pytest.raises(
            UserCodeException,
            match="while executing export_config\\(\\): no config here!",
        ):
            read_config(config_path)
