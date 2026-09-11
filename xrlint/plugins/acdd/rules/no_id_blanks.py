#  Copyright © 2025-2026 Brockmann Consult GmbH and contributors.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from xrlint.node import DatasetNode
from xrlint.plugins.acdd.plugin import plugin
from xrlint.rule import RuleContext, RuleOp


@plugin.define_rule(
    "1.3-no-blanks-in-id",
    version="1.3",
    description="The `id` attribute should not contain blanks.",
    docs_url="https://wiki.esipfed.org/Attribute_Convention_for_Data_Discovery_1-3",
)
class NoBlanksInID(RuleOp):
    def validate_dataset(self, ctx: RuleContext, node: DatasetNode):
        try:
            value = node.dataset.attrs["id"]
        except KeyError:
            ctx.report(
                "Missing attribute 'id'",
                suggestions=["Include a non-blank 'id' attribute in the dataset."],
            )
            return
        if " " in value:
            ctx.report(
                "There should not be blanks in the id field",
                suggestions=["There should not be blanks in the id field"],
            )
