from unittest import TestCase

import pytest
import xarray as xr

# noinspection PyProtectedMember
from xrlint._linter.rulectx import RuleContextImpl
from xrlint.config import ConfigObject
from xrlint.node import DatasetNode
from xrlint.plugins.core.rules.opening_time import OpeningTime
from xrlint.result import Message
from xrlint.rule import RuleExit

valid_dataset_0 = xr.Dataset()

invalid_dataset_0 = xr.Dataset()


class OpeningTimeTest(TestCase):
    @classmethod
    def invoke_op(
        cls, dataset: xr.Dataset, opening_time: float, threshold: float | None = None
    ):
        ctx = RuleContextImpl(
            config=ConfigObject(),
            dataset=dataset,
            file_path="test.zarr",
            file_index=None,
            opening_time=opening_time,
        )
        node = DatasetNode(
            path="dataset",
            parent=None,
            dataset=ctx.dataset,
        )
        rule_op = (
            OpeningTime(threshold=threshold) if threshold is not None else OpeningTime()
        )
        with pytest.raises(RuleExit):
            rule_op.validate_dataset(ctx, node)
        return ctx

    def test_valid(self):
        ctx = self.invoke_op(xr.Dataset(), 1.0, threshold=None)
        self.assertEqual([], ctx.messages)

        ctx = self.invoke_op(xr.Dataset(), 1.0, threshold=1.0)
        self.assertEqual([], ctx.messages)

    def test_invalid(self):
        ctx = self.invoke_op(xr.Dataset(), 3.16, threshold=None)
        self.assertEqual(
            [
                Message(
                    message="Opening time exceeds threshold: 3.2 > 2.5 seconds.",
                    node_path="dataset",
                    severity=2,
                )
            ],
            ctx.messages,
        )

        ctx = self.invoke_op(xr.Dataset(), 0.2032, threshold=0.1)
        self.assertEqual(
            [
                Message(
                    message="Opening time exceeds threshold: 0.2 > 0.1 seconds.",
                    node_path="dataset",
                    severity=2,
                )
            ],
            ctx.messages,
        )
