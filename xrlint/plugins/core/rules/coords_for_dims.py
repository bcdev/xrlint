from xrlint.result import Suggestion
from xrlint.node import DataArrayNode
from xrlint.plugins.core.rules import plugin
from xrlint.rule import RuleContext, RuleOp


@plugin.define_rule(
    "coords-for-dims",
    version="1.0.0",
    description=(
        "Dimensions of data variables should have corresponding coordinates."
    ),
)
class CoordsForDims(RuleOp):
    def data_array(self, ctx: RuleContext, node: DataArrayNode):
        if not node.in_data_vars():
            return
        data_array = node.data_array
        for dim in data_array.dims:
            if dim not in data_array.coords:
                ctx.report(
                    f"Dimension {dim!r} without corresponding coordinate.",
                    suggestions=[
                        Suggestion(
                            f"Add a coordinate variable named {dim!r}"
                            f" with size {data_array.sizes[dim]}."
                        )
                    ],
                )
