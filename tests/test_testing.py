from unittest import TestCase

import pytest
import xarray as xr


from xrlint.testing import RuleTest
from xrlint.testing import RuleTester
from xrlint.node import DatasetNode
from xrlint.rule import RuleContext
from xrlint.rule import RuleOp


class ForceTitle(RuleOp):
    def dataset(self, ctx: RuleContext, node: DatasetNode):
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
        tester = RuleTester(rules={"test/force-title": "error"})
        tester.run(
            "force-title",
            ForceTitle,
            valid=[
                RuleTest(dataset=VALID_DATASET_1),
                RuleTest(dataset=VALID_DATASET_2),
            ],
            invalid=[
                RuleTest(dataset=INVALID_DATASET_1),
                RuleTest(dataset=INVALID_DATASET_2),
            ],
        )

    def test_raises_valid(self):
        tester = RuleTester(rules={"test/force-title": "error"})
        with pytest.raises(
            AssertionError,
            match=(
                "Rule 'force-title': test_valid_2:"
                " expected no problem, but got one error"
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

    def test_raises_invalid(self):
        tester = RuleTester(rules={"test/force-title": "error"})
        with pytest.raises(
            AssertionError,
            match=(
                "Rule 'force-title': test_invalid_1:"
                " expected one or more problems, but got no problems"
            ),
        ):
            tester.run(
                "force-title",
                ForceTitle,
                invalid=[
                    RuleTest(dataset=INVALID_DATASET_1),
                    RuleTest(dataset=VALID_DATASET_1),
                ],
            )
