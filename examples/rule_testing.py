#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

"""
This example demonstrates how to develop new rules.
"""

import xarray as xr

from xrlint.node import DatasetNode
from xrlint.rule import RuleContext, RuleOp, define_rule
from xrlint.testing import RuleTest, RuleTester


# ----------------------------------------------------
# Place the rule implementation code in its own module
# ----------------------------------------------------


@define_rule("good-title")
class GoodTitle(RuleOp):
    """Dataset title should be 'Hello World!'."""

    # We just validate the dataset instance here. You can also implement
    # the validation of other nodes in this class, e.g.,
    # validate_datatree(), validate_variable(), validate_attrs(),
    # and validate_attr().
    #
    def validate_dataset(self, ctx: RuleContext, node: DatasetNode):
        good_title = "Hello World!"
        if node.dataset.attrs.get("title") != good_title:
            ctx.report(
                "Attribute 'title' wrong.",
                suggestions=[f"Rename it to {good_title!r}."],
            )


# ---------------------------------------------------
# Place the following rule test code in a test module
# ---------------------------------------------------

tester = RuleTester()

valid_dataset = xr.Dataset(attrs=dict(title="Hello World!"))
invalid_dataset = xr.Dataset(attrs=dict(title="Hello Hamburg!"))

# You can use the tester to run a test directly
#
tester.run(
    "good-title",
    GoodTitle,
    valid=[RuleTest(dataset=valid_dataset)],
    # We expect one message to be emitted
    invalid=[RuleTest(dataset=invalid_dataset, expected=1)],
)

# ... or generate a test class that will be derived from `unitest.TestCase`.
# This will provide you tooling support via your test runner, e.g., pytest,
# as the tests in `valid` and `invalid` will be transformed into
# test methods of the generated class.
#
GoodTitleTest = tester.define_test(
    "good-title",
    GoodTitle,
    valid=[RuleTest(dataset=valid_dataset)],
    # Note, here we expect a specific message to be emitted
    invalid=[RuleTest(dataset=invalid_dataset, expected=["Attribute 'title' wrong."])],
)
