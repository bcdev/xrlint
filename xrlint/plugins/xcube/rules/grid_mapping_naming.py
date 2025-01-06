from xrlint.node import DatasetNode
from xrlint.plugins.xcube.constants import GM_NAMES, GM_NAMES_TEXT
from xrlint.plugins.xcube.rules import plugin
from xrlint.rule import RuleOp, RuleContext


@plugin.define_rule(
    "grid-mapping-naming",
    version="1.0.0",
    type="suggestion",
    description=(
        f"Grid mapping variables should be called {GM_NAMES_TEXT}"
        f" for compatibility with rioxarray and other packages."
    ),
)
class GridMappingNaming(RuleOp):
    def dataset(self, ctx: RuleContext, node: DatasetNode):
        for var_name, var in node.dataset.variables.items():
            if "grid_mapping_name" in var.attrs and var_name not in GM_NAMES:
                ctx.report(
                    f"Grid mapping variables should be named"
                    f" {GM_NAMES_TEXT},"
                    f" but name is {var_name!r}"
                )
