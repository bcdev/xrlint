"""
This example demonstrates how to develop new rules.
"""

import xarray as xr

from xrlint.node import DatasetNode
from xrlint.rule import RuleContext
from xrlint.rule import RuleOp
from xrlint.rule import define_rule
from xrlint.testing import RuleTest
from xrlint.testing import RuleTester


@define_rule("good-title")
class GoodTitle(RuleOp):
    """Dataset title should be 'Hello World!'."""

    def dataset(self, ctx: RuleContext, node: DatasetNode):
        good_title = "Hello World!"
        if node.dataset.attrs.get("title") != good_title:
            ctx.report(
                "Attribute 'title' wrong.",
                suggestions=[f"Rename it to {good_title!r}."],
            )


# -----------------
# In another module
# -----------------

tester = RuleTester()

valid_dataset = xr.Dataset(attrs=dict(title="Hello World!"))
invalid_dataset = xr.Dataset(attrs=dict(title="Hello Hamburg!"))

# Run test directly
tester.run(
    "good-title",
    GoodTitle,
    valid=[RuleTest(dataset=valid_dataset)],
    invalid=[RuleTest(dataset=invalid_dataset)],
)

# or define a test class derived from unitest.TestCase
GoodTitleTest = tester.define_test(
    "good-title",
    GoodTitle,
    valid=[RuleTest(dataset=valid_dataset)],
    invalid=[RuleTest(dataset=invalid_dataset)],
)
