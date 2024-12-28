from xrlint.node import DataArrayNode
from xrlint.plugins.core.rules import plugin
from xrlint.rule import RuleOp, RuleContext


@plugin.define_rule("var-units-attr", version="1.0.0")
class VarUnitsAttr(RuleOp):
    def data_array(self, ctx: RuleContext, node: DataArrayNode):
        units = node.data_array.attrs.get("units")
        if units is None:
            ctx.report(f"Missing 'units' attribute in variable {node.name!r}.")
        elif not isinstance(units, str):
            ctx.report(f"Invalid 'units' attribute in variable {node.name!r}.")
        elif not units:
            ctx.report(f"Empty 'units' attribute in variable {node.name!r}.")
