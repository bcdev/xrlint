import xrlint.api as xrl
from xrlint.plugins.core.rules import registry


@registry.define_rule(name="var-units-attr", version="1.0.0")
class VarUnitsAttr(xrl.RuleOp):
    def data_array(self, ctx: xrl.RuleContext, node: xrl.DataArrayNode):
        units = node.data_array.attrs.get("units")
        if units is None:
            ctx.report(f"Missing 'units' attribute in variable {node.name!r}.")
        elif not isinstance(units, str):
            ctx.report(f"Invalid 'units' attribute in variable {node.name!r}.")
        elif not units:
            ctx.report(f"Empty 'units' attribute in variable {node.name!r}.")
