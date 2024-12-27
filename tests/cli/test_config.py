from typing import Any
from unittest import TestCase

import fsspec

from xrlint.cli.config import read_config
from xrlint.config import Config, EffectiveConfig
from xrlint.rule import RuleConfig

yaml_text = """
name: yaml-test
rules:
  rule-1: 2
  rule-2: "warn"
  rule-3: ["error", {max_size: 500}]
"""


json_text = """{
    "name": "json-test",
    "rules": {
      "rule-1": 2,
      "rule-2": "warn",
      "rule-3": ["error", {"max_size": 500}]
    }
}
"""

py_text = """
from xrlint.config import Config
from xrlint.rule import RuleConfig

config = Config(
    name="py-test",
    rules={
      "rule-1": RuleConfig(2),
      "rule-2": RuleConfig(1),
      "rule-3": RuleConfig(2, kwargs={"max_size": 500})
    }
)
"""


class CliConfigTest(TestCase):
    def test_read_config_yaml(self):
        config_path = "memory://.xrlintrc.yaml"
        with fsspec.open(config_path, mode="w") as f:
            f.write(yaml_text)

        config = read_config(config_path)
        self.assert_config_ok(config, "yaml-test")

    def test_read_config_json(self):
        config_path = "memory://.xrlintrc.json"
        with fsspec.open(config_path, mode="w") as f:
            f.write(json_text)

        config = read_config(config_path)
        self.assert_config_ok(config, "json-test")

    def test_read_config_python(self):
        import os

        dir_path = os.path.dirname(__file__)
        config_path = f"{dir_path}/xrlintrc.py"
        with open(config_path, mode="w") as f:
            f.write(py_text)
        try:
            config = read_config(config_path)
            self.assert_config_ok(config, "py-test")
        finally:
            os.remove(config_path)

    def assert_config_ok(self, config: Any, name: str):
        self.assertEqual(
            EffectiveConfig(
                common=Config(
                    name=name,
                    rules={
                        "rule-1": RuleConfig(2),
                        "rule-2": RuleConfig(1),
                        "rule-3": RuleConfig(2, kwargs={"max_size": 500}),
                    },
                )
            ),
            config,
        )
