#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from xrlint.node import DatasetNode
from xrlint.plugins.xcube.plugin import plugin
from xrlint.plugins.xcube.util import is_spatial_var
from xrlint.rule import RuleContext, RuleOp


@plugin.define_rule(
    "any-spatial-data-var",
    version="1.0.0",
    type="problem",
    description="A datacube should have spatial data variables.",
    docs_url=(
        "https://xcube.readthedocs.io/en/latest/cubespec.html#data-model-and-format"
    ),
)
class AnySpatialDataVar(RuleOp):
    def validate_dataset(self, ctx: RuleContext, node: DatasetNode):
        if not any(map(is_spatial_var, node.dataset.data_vars.values())):
            ctx.report("No spatial data variables found.")
