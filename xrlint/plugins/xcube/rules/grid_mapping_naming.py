#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from xrlint.node import DatasetNode
from xrlint.plugins.xcube.constants import GM_NAMES, GM_NAMES_TEXT
from xrlint.plugins.xcube.plugin import plugin
from xrlint.rule import RuleContext, RuleOp


@plugin.define_rule(
    "grid-mapping-naming",
    version="1.0.0",
    type="suggestion",
    description=(
        f"Grid mapping variables should be called {GM_NAMES_TEXT}"
        f" for compatibility with rioxarray and other packages."
    ),
    docs_url="https://xcube.readthedocs.io/en/latest/cubespec.html#spatial-reference",
)
class GridMappingNaming(RuleOp):
    def validate_dataset(self, ctx: RuleContext, node: DatasetNode):
        for var_name, var in node.dataset.variables.items():
            if "grid_mapping_name" in var.attrs and var_name not in GM_NAMES:
                ctx.report(
                    f"Grid mapping variables should be named"
                    f" {GM_NAMES_TEXT},"
                    f" but name is {var_name!r}."
                )
