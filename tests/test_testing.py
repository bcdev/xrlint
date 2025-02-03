#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from unittest import TestCase

import pytest
import xarray as xr

from xrlint.node import DatasetNode
from xrlint.rule import RuleContext, RuleOp
from xrlint.testing import RuleTest, RuleTester


class ForceTitle(RuleOp):
    def validate_dataset(self, ctx: RuleContext, node: DatasetNode):
        title = node.dataset.attrs.get("title")
        if not title:
            ctx.report("Datasets must have a title")


VALID_DATASET_1 = xr.Dataset(attrs=dict(title="OC-Climatology"))
VALID_DATASET_2 = xr.Dataset(attrs=dict(title="SST-Climatology"))
INVALID_DATASET_1 = xr.Dataset()
INVALID_DATASET_2 = xr.Dataset(attrs=dict(title=""))


# noinspection PyMethodMayBeStatic
class RuleTesterTest(TestCase):
    def test_ok(self):
        tester = RuleTester(rules={"testing/force-title": "error"})
        tester.run(
            "force-title",
            ForceTitle,
            valid=[
                RuleTest(dataset=VALID_DATASET_1),
                RuleTest(dataset=VALID_DATASET_2),
            ],
            invalid=[
                RuleTest(dataset=INVALID_DATASET_1, expected=1),
                RuleTest(
                    dataset=INVALID_DATASET_2, expected=["Datasets must have a title"]
                ),
            ],
        )

    def test_raises_valid(self):
        tester = RuleTester(rules={"testing/force-title": "error"})
        with pytest.raises(
            AssertionError,
            match=(
                "Rule 'force-title': test_valid_2:"
                " expected no problems, but got one error:\nActual message:\n"
                "  0: Datasets must have a title"
            ),
        ):
            tester.run(
                "force-title",
                ForceTitle,
                valid=[
                    RuleTest(dataset=VALID_DATASET_1),
                    RuleTest(dataset=VALID_DATASET_2),
                    RuleTest(dataset=INVALID_DATASET_1),
                ],
            )

    def test_raises_invalid_with_count(self):
        tester = RuleTester(rules={"testing/force-title": "error"})
        with pytest.raises(
            AssertionError,
            match=(
                "Rule 'force-title': test_invalid_0:"
                " expected one problem, but got no problems."
            ),
        ):
            tester.run(
                "force-title",
                ForceTitle,
                invalid=[
                    RuleTest(dataset=VALID_DATASET_1, expected=1),
                ],
            )

    def test_raises_valid_with_count(self):
        tester = RuleTester(rules={"testing/force-title": "error"})
        with pytest.raises(
            AssertionError,
            match=(
                "Rule 'force-title':"
                " test_invalid_raises_valid_with_count:"
                " expected one problem, but got no problems."
            ),
        ):
            tester.run(
                "force-title",
                ForceTitle,
                invalid=[
                    RuleTest(
                        dataset=VALID_DATASET_1,
                        expected=1,
                        name="raises_valid_with_count",
                    ),
                ],
            )

    def test_raises_invalid_with_matching_message(self):
        tester = RuleTester(rules={"testing/force-title": "error"})
        with pytest.raises(
            AssertionError,
            match=(
                "Rule 'force-title':"
                " test_invalid_raises_invalid_with_matching_message:"
                " expected one problem, but got no problems:\n"
                "Expected message:\n"
                "  0: Datasets must have a title"
            ),
        ):
            tester.run(
                "force-title",
                ForceTitle,
                invalid=[
                    RuleTest(
                        dataset=VALID_DATASET_1,
                        expected=["Datasets must have a title"],
                        name="raises_invalid_with_matching_message",
                    ),
                ],
            )

    def test_raises_invalid_with_mismatching_message(self):
        tester = RuleTester(rules={"testing/force-title": "error"})
        with pytest.raises(
            AssertionError,
            match=(
                "Rule 'force-title':"
                " test_invalid_raises_invalid_with_mismatching_message:"
                " got one error as expected, but encountered message mismatch:\n"
                "Message 0:\n"
                "  Expected: Batasets bust bave a bitle\n"
                "  Actual: Datasets must have a title"
            ),
        ):
            tester.run(
                "force-title",
                ForceTitle,
                invalid=[
                    RuleTest(
                        dataset=INVALID_DATASET_1,
                        expected=["Batasets bust bave a bitle"],
                        name="raises_invalid_with_mismatching_message",
                    ),
                ],
            )
