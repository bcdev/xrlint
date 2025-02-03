#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from xrlint.node import DatasetNode
from xrlint.plugins.xcube.plugin import plugin
from xrlint.rule import RuleContext, RuleOp


@plugin.define_rule(
    "dataset-title",
    version="1.0.0",
    type="problem",
    description="Datasets should be given a non-empty title.",
    docs_url="https://xcube.readthedocs.io/en/latest/cubespec.html#metadata",
)
class DatasetTitle(RuleOp):
    def validate_dataset(self, ctx: RuleContext, node: DatasetNode):
        attrs = node.dataset.attrs
        if "title" not in attrs:
            ctx.report("Missing attribute 'title'.")
        elif not attrs["title"]:
            ctx.report(f"Invalid attribute 'title': {attrs['title']!r}")
