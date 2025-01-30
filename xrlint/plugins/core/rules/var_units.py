from xrlint.node import VariableNode
from xrlint.plugins.core.plugin import plugin
from xrlint.rule import RuleContext, RuleOp


@plugin.define_rule(
    "var-units",
    version="1.0.0",
    type="suggestion",
    description="Every variable should provide a description of its units.",
    docs_url="https://cfconventions.org/cf-conventions/cf-conventions.html#units",
)
class VarUnits(RuleOp):
    def validate_variable(self, ctx: RuleContext, node: VariableNode):
        data_array = node.array
        units = data_array.attrs.get("units")
        if units is None:
            if "grid_mapping_name" not in data_array.attrs:
                ctx.report(f"Missing 'units' attribute in variable {node.name!r}.")
        elif not isinstance(units, str):
            ctx.report(f"Invalid 'units' attribute in variable {node.name!r}.")
        elif not units:
            ctx.report(f"Empty 'units' attribute in variable {node.name!r}.")
