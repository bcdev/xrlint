from xrlint.node import DataArrayNode
from xrlint.plugins.core.rules import plugin
from xrlint.rule import RuleOp, RuleContext


@plugin.define_rule(
    "var-units-attr",
    version="1.0.0",
    type="suggestion",
    description="Every variable should have a valid 'units' attribute.",
)
class VarUnitsAttr(RuleOp):
    def data_array(self, ctx: RuleContext, node: DataArrayNode):
        data_array = node.data_array
        units = data_array.attrs.get("units")
        if units is None:
            if "grid_mapping_name" not in data_array.attrs:
                ctx.report(f"Missing 'units' attribute in variable {node.name!r}.")
        elif not isinstance(units, str):
            ctx.report(f"Invalid 'units' attribute in variable {node.name!r}.")
        elif not units:
            ctx.report(f"Empty 'units' attribute in variable {node.name!r}.")
