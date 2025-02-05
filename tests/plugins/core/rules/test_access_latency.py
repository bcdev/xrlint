#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from unittest import TestCase

import pytest
import xarray as xr

# noinspection PyProtectedMember
from xrlint._linter.rulectx import RuleContextImpl
from xrlint.config import ConfigObject
from xrlint.constants import DATASET_ROOT_NAME
from xrlint.node import DatasetNode
from xrlint.plugins.core.rules.access_latency import AccessLatency
from xrlint.result import Message
from xrlint.rule import RuleExit

valid_dataset_0 = xr.Dataset()

invalid_dataset_0 = xr.Dataset()


class OpeningTimeTest(TestCase):
    @classmethod
    def invoke_op(
        cls, dataset: xr.Dataset, access_latency: float, threshold: float | None = None
    ):
        ctx = RuleContextImpl(
            config=ConfigObject(),
            dataset=dataset,
            file_path="test.zarr",
            file_index=None,
            access_latency=access_latency,
        )
        node = DatasetNode(
            parent=None,
            path=DATASET_ROOT_NAME,
            name=DATASET_ROOT_NAME,
            dataset=ctx.dataset,
        )
        rule_op = (
            AccessLatency(threshold=threshold)
            if threshold is not None
            else AccessLatency()
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
                    message="Access latency exceeds threshold: 3.2 > 2.5 seconds.",
                    node_path=DATASET_ROOT_NAME,
                    severity=2,
                )
            ],
            ctx.messages,
        )

        ctx = self.invoke_op(xr.Dataset(), 0.2032, threshold=0.1)
        self.assertEqual(
            [
                Message(
                    message="Access latency exceeds threshold: 0.2 > 0.1 seconds.",
                    node_path=DATASET_ROOT_NAME,
                    severity=2,
                )
            ],
            ctx.messages,
        )
