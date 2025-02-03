#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from xrlint.node import VariableNode
from xrlint.plugins.core.plugin import plugin
from xrlint.rule import RuleContext, RuleOp
from xrlint.util.schema import schema

DEFAULT_ATTRS = ["standard_name", "long_name"]


@plugin.define_rule(
    "var-desc",
    version="1.0.0",
    type="suggestion",
    description=(
        "Check that each data variable provides an"
        " identification and description of the content."
        " The rule can be configured by parameter `attrs` which is a list"
        " of names of attributes that provides descriptive information."
        f" It defaults to `{DEFAULT_ATTRS}`."
        ""
    ),
    docs_url=(
        "https://cfconventions.org/cf-conventions/cf-conventions.html#standard-name"
    ),
    schema=schema(
        "object",
        properties={
            "attrs": schema(
                "array",
                items=schema("string"),
                default=DEFAULT_ATTRS,
                title="Attribute names to check",
            ),
        },
    ),
)
class VarDesc(RuleOp):
    def __init__(self, attrs: list[str] | None = None):
        self._attrs = attrs if attrs is not None else DEFAULT_ATTRS

    def validate_variable(self, ctx: RuleContext, node: VariableNode):
        if node.name not in ctx.dataset.data_vars:
            # This rule applies to data variables only
            return

        var_attrs = node.array.attrs
        for attr_name in self._attrs:
            if attr_name not in var_attrs:
                ctx.report(f"Missing attribute {attr_name!r}.")
