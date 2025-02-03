#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from xrlint.node import DatasetNode
from xrlint.plugins.xcube.constants import TIME_NAME
from xrlint.plugins.xcube.plugin import plugin
from xrlint.plugins.xcube.util import get_dataset_level_info, is_spatial_var
from xrlint.rule import RuleContext, RuleOp
from xrlint.util.formatting import format_seq


@plugin.define_rule(
    "ml-dataset-time",
    version="1.0.0",
    type="problem",
    description=(
        "The `time` dimension of multi-level datasets should use a chunk size of 1."
        " This allows for faster image tile generation for visualisation."
    ),
    docs_url="https://xcube.readthedocs.io/en/latest/mldatasets.html#definition",
)
class MLDatasetTime(RuleOp):
    def validate_dataset(self, ctx: RuleContext, node: DatasetNode):
        level_info = get_dataset_level_info(node.dataset)
        if level_info is None:
            # ok, this rules applies only to level datasets opened
            # by the xcube multi-level processor
            return

        if TIME_NAME not in node.dataset.sizes or node.dataset.sizes[TIME_NAME] <= 1:
            # ok, no time dimension used or no time extent
            return

        for var_name, var in node.dataset.data_vars.items():
            if is_spatial_var(var) and TIME_NAME in var.dims and var.chunks is not None:
                time_index = var.dims.index(TIME_NAME)
                time_chunks = var.chunks[time_index]
                if not all(c == 1 for c in time_chunks):
                    ctx.report(
                        f"Variable {var_name!r} uses chunking for {TIME_NAME!r}"
                        f" that differs from from one: {format_seq(time_chunks)}."
                    )
