from xrlint.node import DatasetNode
from xrlint.plugins.xcube.rules import plugin
from xrlint.plugins.xcube.util import is_spatial_var
from xrlint.rule import RuleOp, RuleContext


@plugin.define_rule(
    "any-spatial-data-var",
    version="1.0.0",
    type="problem",
    description="A datacube should have spatial data variables.",
)
class AnySpatialDataVar(RuleOp):
    def dataset(self, ctx: RuleContext, node: DatasetNode):
        if not any(map(is_spatial_var, node.dataset.data_vars.values())):
            ctx.report("No spatial data variables found.")
