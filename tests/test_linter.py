from typing import Any
from unittest import TestCase

import xarray as xr

from xrlint.config import Config
from xrlint.constants import CORE_PLUGIN_NAME
from xrlint.linter import Linter
from xrlint.linter import new_linter
from xrlint.plugin import Plugin
from xrlint.plugin import PluginMeta
from xrlint.node import (
    AttrsNode,
    AttrNode,
    DataArrayNode,
    DatasetNode,
)
from xrlint.processor import ProcessorOp
from xrlint.result import Message
from xrlint.result import Result
from xrlint.rule import RuleContext
from xrlint.rule import RuleExit
from xrlint.rule import RuleOp


class LinterTest(TestCase):
    def test_default_config_is_empty(self):
        linter = Linter()
        self.assertEqual(Config(), linter.config)

    def test_new_linter(self):
        import xrlint.all as xrl

        linter = new_linter()
        self.assertIsInstance(linter, xrl.Linter)
        self.assertIsInstance(linter.config.plugins, dict)
        self.assertEqual({CORE_PLUGIN_NAME}, set(linter.config.plugins.keys()))
        self.assertEqual(None, linter.config.rules)

        linter = new_linter(recommended=False)
        self.assertIsInstance(linter, xrl.Linter)
        self.assertIsInstance(linter.config.plugins, dict)
        self.assertEqual({CORE_PLUGIN_NAME}, set(linter.config.plugins.keys()))
        self.assertEqual(None, linter.config.rules)

        linter = new_linter(recommended=True)
        self.assertIsInstance(linter, xrl.Linter)
        self.assertIsInstance(linter.config.plugins, dict)
        self.assertEqual({CORE_PLUGIN_NAME}, set(linter.config.plugins.keys()))
        self.assertIsInstance(linter.config.rules, dict)
        self.assertIn("coords-for-dims", linter.config.rules)


class LinterVerifyTest(TestCase):

    def setUp(self):

        plugin = Plugin(meta=PluginMeta(name="test"))

        @plugin.define_rule("no-space-in-attr-name")
        class AttrVer(RuleOp):
            def attr(self, ctx: RuleContext, node: AttrNode):
                if " " in node.name:
                    ctx.report(f"Attribute name with space: {node.name!r}")

        @plugin.define_rule("no-empty-attrs")
        class AttrsVer(RuleOp):
            def attrs(self, ctx: RuleContext, node: AttrsNode):
                if not node.attrs:
                    ctx.report("Empty attributes")

        @plugin.define_rule("data-var-dim-must-have-coord")
        class DataArrayVer(RuleOp):
            def data_array(self, ctx: RuleContext, node: DataArrayNode):
                if node.in_data_vars():
                    for dim_name in node.data_array.dims:
                        if dim_name not in ctx.dataset.coords:
                            ctx.report(
                                f"Dimension {dim_name!r}"
                                f" of data variable {node.name!r}"
                                f" is missing a coordinate variable"
                            )

        @plugin.define_rule("dataset-without-data-vars")
        class DatasetVer(RuleOp):
            def dataset(self, ctx: RuleContext, node: DatasetNode):
                if len(node.dataset.data_vars) == 0:
                    ctx.report("Dataset does not have data variables")
                    raise RuleExit  # no need to traverse further

        @plugin.define_processor("multi-level-dataset")
        class MultiLevelDataset(ProcessorOp):
            def preprocess(
                self, file_path: str, _opener_options: dict[str, Any]
            ) -> list[tuple[xr.Dataset, str]]:
                return [
                    (xr.Dataset(attrs={"title": "Level 0"}), file_path + "/0.zarr"),
                    (xr.Dataset(attrs={"title": "Level 1"}), file_path + "/1.zarr"),
                ]

            def postprocess(
                self, messages: list[list[Message]], file_path: str
            ) -> list[Message]:
                return messages[0] + messages[1]

        config = Config(plugins={"test": plugin})
        self.linter = Linter(config=config)
        super().setUp()

    def test_rules_are_ok(self):
        self.assertEqual(
            [
                "no-space-in-attr-name",
                "no-empty-attrs",
                "data-var-dim-must-have-coord",
                "dataset-without-data-vars",
            ],
            list(self.linter._config.plugins["test"].rules.keys()),
        )

    def test_linter_respects_rule_severity_error(self):
        result = self.linter.verify_dataset(
            xr.Dataset(), rules={"test/dataset-without-data-vars": 2}
        )
        self.assertEqual(
            Result(
                result.config,
                file_path="<dataset>",
                warning_count=0,
                error_count=1,
                fatal_error_count=0,
                fixable_warning_count=0,
                fixable_error_count=0,
                messages=[
                    Message(
                        message="Dataset does not have data variables",
                        node_path="dataset",
                        rule_id="test/dataset-without-data-vars",
                        severity=2,
                    )
                ],
            ),
            result,
        )

    def test_linter_respects_rule_severity_warn(self):
        result = self.linter.verify_dataset(
            xr.Dataset(), rules={"test/dataset-without-data-vars": 1}
        )
        self.assertEqual(
            Result(
                result.config,
                file_path="<dataset>",
                warning_count=1,
                error_count=0,
                fatal_error_count=0,
                fixable_warning_count=0,
                fixable_error_count=0,
                messages=[
                    Message(
                        message="Dataset does not have data variables",
                        node_path="dataset",
                        rule_id="test/dataset-without-data-vars",
                        severity=1,
                    )
                ],
            ),
            result,
        )

    def test_linter_respects_rule_severity_off(self):
        result = self.linter.verify_dataset(
            xr.Dataset(), rules={"test/dataset-without-data-vars": 0}
        )
        self.assertEqual(
            Result(
                result.config,
                file_path="<dataset>",
                warning_count=0,
                error_count=0,
                fatal_error_count=0,
                fixable_warning_count=0,
                fixable_error_count=0,
                messages=[],
            ),
            result,
        )

    def test_linter_real_life_scenario(self):
        dataset = xr.Dataset(
            attrs={
                # issue #1: space in attr name
                "created at": "10:20"
            },
            data_vars={
                "chl": (
                    xr.DataArray(
                        [[[1, 2], [3, 4]]],
                        dims=["time", "y", "x"],
                        attrs={"units": "mg/m^-3"},
                    )
                ),
                # issue #2: attrs missing
                "tsm": xr.DataArray([[[1, 2], [3, 4]]], dims=["time", "y", "x"]),
            },
            coords={
                "x": xr.DataArray([0.1, 0.2], dims="x", attrs={"units": "m"}),
                "y": xr.DataArray([0.2, 0.3], dims="y", attrs={"units": "m"}),
                # issue #3 + #4: missing "time" coord
            },
        )
        dataset.encoding["source"] = "chl-tsm.zarr"

        result = self.linter.verify_dataset(
            dataset,
            rules={
                "test/no-space-in-attr-name": "error",
                "test/no-empty-attrs": "warn",
                "test/data-var-dim-must-have-coord": "error",
                "test/dataset-without-data-vars": "warn",
            },
        )
        self.assertEqual(
            Result(
                result.config,
                file_path="chl-tsm.zarr",
                warning_count=1,
                error_count=3,
                fatal_error_count=0,
                fixable_warning_count=0,
                fixable_error_count=0,
                messages=[
                    Message(
                        message="Attribute name with space: 'created at'",
                        node_path="dataset.attrs['created at']",
                        rule_id="test/no-space-in-attr-name",
                        severity=2,
                    ),
                    Message(
                        message="Empty attributes",
                        node_path="dataset.data_vars['tsm'].attrs",
                        rule_id="test/no-empty-attrs",
                        severity=1,
                    ),
                    Message(
                        message=(
                            "Dimension 'time' of data "
                            "variable 'chl' is missing a "
                            "coordinate variable"
                        ),
                        node_path="dataset.data_vars['chl']",
                        rule_id="test/data-var-dim-must-have-coord",
                        severity=2,
                    ),
                    Message(
                        message=(
                            "Dimension 'time' of data "
                            "variable 'tsm' is missing a "
                            "coordinate variable"
                        ),
                        node_path="dataset.data_vars['tsm']",
                        rule_id="test/data-var-dim-must-have-coord",
                        severity=2,
                    ),
                ],
            ),
            result,
        )

    def test_processor(self):

        result = self.linter.verify_dataset(
            "test.levels",
            config=Config.from_value(
                {
                    "processor": "test/multi-level-dataset",
                    "rules": {"test/dataset-without-data-vars": "warn"},
                }
            ),
        )

        self.assertEqual(
            [
                Message(
                    message="Dataset does not have data variables",
                    node_path="dataset",
                    rule_id="test/dataset-without-data-vars",
                    severity=1,
                ),
                Message(
                    message="Dataset does not have data variables",
                    node_path="dataset",
                    rule_id="test/dataset-without-data-vars",
                    severity=1,
                ),
            ],
            result.messages,
        )
