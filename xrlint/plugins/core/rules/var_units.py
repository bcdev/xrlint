#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

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
        array = node.array
        attrs = array.attrs

        if "grid_mapping_name" in attrs:
            # likely grid mapping variable --> rule "gid-mappings"
            return
        if "units" in array.encoding:
            # likely time coordinate --> rule "time-coordinate"
            return

        units = attrs.get("units")
        if "units" not in attrs:
            ctx.report("Missing attribute 'units'.")
        elif not isinstance(units, str):
            ctx.report(f"Invalid attribute 'units': {units!r}")
        elif not units:
            ctx.report("Empty attribute 'units'.")
