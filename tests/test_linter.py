#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from typing import Any
from unittest import TestCase

import xarray as xr

from xrlint.config import Config, ConfigObject
from xrlint.constants import CORE_PLUGIN_NAME, DATASET_ROOT_NAME
from xrlint.linter import Linter, new_linter
from xrlint.node import AttrNode, AttrsNode, DatasetNode, DataTreeNode, VariableNode
from xrlint.plugin import new_plugin
from xrlint.processor import ProcessorOp
from xrlint.result import Message, Result
from xrlint.rule import RuleContext, RuleExit, RuleOp


class LinterTest(TestCase):
    def test_default_config_is_empty(self):
        linter = Linter()
        self.assertEqual(Config(), linter.config)

    def test_new_linter(self):
        linter = new_linter()
        self.assertIsInstance(linter, Linter)
        self.assertEqual(1, len(linter.config.objects))
        config_obj = linter.config.objects[0]
        self.assertIsInstance(config_obj.plugins, dict)
        self.assertEqual({CORE_PLUGIN_NAME}, set(config_obj.plugins.keys()))
        self.assertEqual(None, config_obj.rules)

    def test_new_linter_recommended(self):
        linter = new_linter("recommended")
        self.assertIsInstance(linter, Linter)
        self.assertEqual(2, len(linter.config.objects))
        config_obj_0 = linter.config.objects[0]
        config_obj_1 = linter.config.objects[1]
        self.assertIsInstance(config_obj_0.plugins, dict)
        self.assertEqual({CORE_PLUGIN_NAME}, set(config_obj_0.plugins.keys()))
        self.assertIsInstance(config_obj_1.rules, dict)
        self.assertIn("coords-for-dims", config_obj_1.rules)

    def test_new_linter_all(self):
        linter = new_linter("all")
        self.assertIsInstance(linter, Linter)
        self.assertEqual(2, len(linter.config.objects))
        config_obj_0 = linter.config.objects[0]
        config_obj_1 = linter.config.objects[1]
        self.assertIsInstance(config_obj_0.plugins, dict)
        self.assertEqual({CORE_PLUGIN_NAME}, set(config_obj_0.plugins.keys()))
        self.assertIsInstance(config_obj_1.rules, dict)
        self.assertIn("coords-for-dims", config_obj_1.rules)


class LinterValidateWithConfigTest(TestCase):
    def test_config_with_config_list(self):
        linter = new_linter()
        result = linter.validate(
            xr.Dataset(),
            config=Config.from_value([{"rules": {"no-empty-attrs": 2}}]),
        )
        self.assert_result_ok(result, "Missing metadata, attributes are empty.")

    def test_config_with_list_of_config(self):
        linter = new_linter()
        result = linter.validate(
            xr.Dataset(),
            config=[{"rules": {"no-empty-attrs": 2}}],
        )
        self.assert_result_ok(result, "Missing metadata, attributes are empty.")

    def test_config_with_config_obj(self):
        linter = new_linter()
        result = linter.validate(
            xr.Dataset(),
            config={"rules": {"no-empty-attrs": 2}},
        )
        self.assert_result_ok(result, "Missing metadata, attributes are empty.")

    def test_config_with_file_not_found(self):
        linter = new_linter({"rules": {"no-empty-attrs": 2}})
        result = linter.validate("cube.nc")
        self.assert_result_ok(result, "No such file or directory:")

    def test_no_config(self):
        linter = Linter()
        result = linter.validate(xr.Dataset())
        self.assert_result_ok(result, "No configuration given or matches '<dataset>'.")

    def assert_result_ok(self, result: Result, expected_message: str):
        self.assertIsInstance(result, Result)
        self.assertEqual(1, len(result.messages))
        self.assertEqual(2, result.messages[0].severity)
        self.assertIn(expected_message, result.messages[0].message)


class LinterValidateTest(TestCase):
    # noinspection PyUnusedLocal
    def setUp(self):
        plugin = new_plugin(name="test")

        @plugin.define_rule("no-space-in-attr-name")
        class AttrVer(RuleOp):
            def validate_attr(self, ctx: RuleContext, node: AttrNode):
                if " " in node.name:
                    ctx.report(f"Attribute name with space: {node.name!r}")

        @plugin.define_rule("no-empty-attrs")
        class AttrsVer(RuleOp):
            def validate_attrs(self, ctx: RuleContext, node: AttrsNode):
                if not node.attrs:
                    ctx.report("Empty attributes")

        @plugin.define_rule("data-var-dim-must-have-coord")
        class VariableVer(RuleOp):
            def validate_variable(self, ctx: RuleContext, node: VariableNode):
                if node.in_data_vars():
                    for dim_name in node.array.dims:
                        if dim_name not in ctx.dataset.coords:
                            ctx.report(
                                f"Dimension {dim_name!r}"
                                f" of data variable {node.name!r}"
                                f" is missing a coordinate variable"
                            )

        @plugin.define_rule("dataset-without-data-vars")
        class DatasetVer(RuleOp):
            def validate_dataset(self, ctx: RuleContext, node: DatasetNode):
                if len(node.dataset.data_vars) == 0:
                    ctx.report("Dataset does not have data variables")
                    raise RuleExit  # no need to traverse further

        @plugin.define_rule("datatree-without-data-vars")
        class DataTreeVer(RuleOp):
            def validate_datatree(self, ctx: RuleContext, node: DataTreeNode):
                if len(node.datatree.data_vars) == 0:
                    ctx.report("DataTree does not have data variables")

        @plugin.define_processor("multi-level-dataset")
        class MultiLevelDataset(ProcessorOp):
            def preprocess(
                self, file_path: str, _opener_options: dict[str, Any]
            ) -> list[tuple[xr.Dataset, str]]:
                if file_path == "bad.levels":
                    raise OSError("bad checksum")
                return [
                    (xr.Dataset(attrs={"title": "Level 0"}), file_path + "/0.zarr"),
                    (xr.Dataset(attrs={"title": "Level 1"}), file_path + "/1.zarr"),
                ]

            def postprocess(
                self, messages: list[list[Message]], file_path: str
            ) -> list[Message]:
                return messages[0] + messages[1]

        config = ConfigObject(plugins={"test": plugin})
        self.linter = Linter(config)
        super().setUp()

    def test_rules_are_ok(self):
        self.assertEqual(
            [
                "no-space-in-attr-name",
                "no-empty-attrs",
                "data-var-dim-must-have-coord",
                "dataset-without-data-vars",
                "datatree-without-data-vars",
            ],
            list(self.linter.config.objects[0].plugins["test"].rules.keys()),
        )

    def test_linter_respects_rule_severity_error(self):
        result = self.linter.validate(
            xr.Dataset(), rules={"test/dataset-without-data-vars": 2}
        )
        self.assertEqual(
            Result(
                config_object=result.config_object,
                file_path="<dataset>",
                messages=[
                    Message(
                        message="Dataset does not have data variables",
                        node_path=DATASET_ROOT_NAME,
                        rule_id="test/dataset-without-data-vars",
                        severity=2,
                    )
                ],
            ),
            result,
        )
        self.assertEqual(0, result.warning_count)
        self.assertEqual(1, result.error_count)
        self.assertEqual(0, result.fatal_error_count)

    def test_linter_respects_rule_severity_warn(self):
        result = self.linter.validate(
            xr.Dataset(), rules={"test/dataset-without-data-vars": 1}
        )
        self.assertEqual(
            Result(
                config_object=result.config_object,
                file_path="<dataset>",
                messages=[
                    Message(
                        message="Dataset does not have data variables",
                        node_path=DATASET_ROOT_NAME,
                        rule_id="test/dataset-without-data-vars",
                        severity=1,
                    )
                ],
            ),
            result,
        )
        self.assertEqual(1, result.warning_count)
        self.assertEqual(0, result.error_count)
        self.assertEqual(0, result.fatal_error_count)

    def test_linter_respects_rule_severity_off(self):
        result = self.linter.validate(
            xr.Dataset(), rules={"test/dataset-without-data-vars": 0}
        )
        self.assertEqual(
            Result(
                config_object=result.config_object,
                file_path="<dataset>",
                messages=[],
            ),
            result,
        )
        self.assertEqual(0, result.warning_count)
        self.assertEqual(0, result.error_count)
        self.assertEqual(0, result.fatal_error_count)

    def test_linter_recognized_unknown_rule(self):
        result = self.linter.validate(xr.Dataset(), rules={"test/dataset-is-fast": 2})
        self.assertEqual(
            [
                Message(
                    message="unknown rule 'test/dataset-is-fast'",
                    rule_id="test/dataset-is-fast",
                    node_path=DATASET_ROOT_NAME,
                    severity=2,
                    fatal=True,
                )
            ],
            result.messages,
        )

    def test_linter_recognized_datatree_rule(self):
        result = self.linter.validate(
            xr.DataTree(
                children={
                    "measurement": xr.DataTree(
                        children={
                            "r10m": xr.DataTree(),
                            "r20m": xr.DataTree(),
                            "r60m": xr.DataTree(),
                        }
                    )
                }
            ),
            rules={"test/datatree-without-data-vars": 2},
        )
        self.assertEqual(
            [
                Message(
                    message="DataTree does not have data variables",
                    node_path="dt",
                    rule_id="test/datatree-without-data-vars",
                    severity=2,
                    fatal=None,
                    fix=None,
                    suggestions=None,
                ),
                Message(
                    message="DataTree does not have data variables",
                    node_path="dt/measurement",
                    rule_id="test/datatree-without-data-vars",
                    severity=2,
                    fatal=None,
                    fix=None,
                    suggestions=None,
                ),
                Message(
                    message="DataTree does not have data variables",
                    node_path="dt/measurement/r10m",
                    rule_id="test/datatree-without-data-vars",
                    severity=2,
                ),
                Message(
                    message="DataTree does not have data variables",
                    node_path="dt/measurement/r20m",
                    rule_id="test/datatree-without-data-vars",
                    severity=2,
                ),
                Message(
                    message="DataTree does not have data variables",
                    node_path="dt/measurement/r60m",
                    rule_id="test/datatree-without-data-vars",
                    severity=2,
                ),
            ],
            result.messages,
        )
        self.assertEqual(0, result.warning_count)
        self.assertEqual(5, result.error_count)
        self.assertEqual(0, result.fatal_error_count)

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

        result = self.linter.validate(
            dataset,
            config={
                "rules": {
                    "test/no-space-in-attr-name": "error",
                    "test/no-empty-attrs": "warn",
                    "test/data-var-dim-must-have-coord": "error",
                    "test/dataset-without-data-vars": "warn",
                },
            },
        )
        self.assertEqual(
            Result(
                config_object=result.config_object,
                file_path="chl-tsm.zarr",
                messages=[
                    Message(
                        message="Attribute name with space: 'created at'",
                        node_path=f"{DATASET_ROOT_NAME}.attrs['created at']",
                        rule_id="test/no-space-in-attr-name",
                        severity=2,
                    ),
                    Message(
                        message="Empty attributes",
                        node_path=f"{DATASET_ROOT_NAME}.data_vars['tsm'].attrs",
                        rule_id="test/no-empty-attrs",
                        severity=1,
                    ),
                    Message(
                        message=(
                            "Dimension 'time' of data "
                            "variable 'chl' is missing a "
                            "coordinate variable"
                        ),
                        node_path=f"{DATASET_ROOT_NAME}.data_vars['chl']",
                        rule_id="test/data-var-dim-must-have-coord",
                        severity=2,
                    ),
                    Message(
                        message=(
                            "Dimension 'time' of data "
                            "variable 'tsm' is missing a "
                            "coordinate variable"
                        ),
                        node_path=f"{DATASET_ROOT_NAME}.data_vars['tsm']",
                        rule_id="test/data-var-dim-must-have-coord",
                        severity=2,
                    ),
                ],
            ),
            result,
        )
        self.assertEqual(1, result.warning_count)
        self.assertEqual(3, result.error_count)
        self.assertEqual(0, result.fatal_error_count)

    def test_processor_ok(self):
        result = self.linter.validate(
            "test.levels",
            config={
                "processor": "test/multi-level-dataset",
                "rules": {"test/dataset-without-data-vars": "warn"},
            },
        )

        self.assertEqual(
            [
                Message(
                    message="Dataset does not have data variables",
                    node_path=f"{DATASET_ROOT_NAME}[0]",
                    rule_id="test/dataset-without-data-vars",
                    severity=1,
                ),
                Message(
                    message="Dataset does not have data variables",
                    node_path=f"{DATASET_ROOT_NAME}[1]",
                    rule_id="test/dataset-without-data-vars",
                    severity=1,
                ),
            ],
            result.messages,
        )

    def test_processor_fail(self):
        result = self.linter.validate(
            "bad.levels",
            config={
                "processor": "test/multi-level-dataset",
                "rules": {"test/dataset-without-data-vars": "warn"},
            },
        )

        self.assertEqual(
            [
                Message(
                    message="bad checksum",
                    severity=2,
                    fatal=True,
                    node_path=DATASET_ROOT_NAME,
                )
            ],
            result.messages,
        )
