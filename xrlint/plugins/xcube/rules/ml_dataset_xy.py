#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

import math

from xrlint.node import DatasetNode
from xrlint.plugins.xcube.plugin import plugin
from xrlint.plugins.xcube.util import get_dataset_level_info, get_spatial_size
from xrlint.rule import RuleContext, RuleOp


@plugin.define_rule(
    "ml-dataset-xy",
    version="1.0.0",
    type="problem",
    description=(
        "Multi-level dataset levels should provide spatial resolutions"
        " decreasing by powers of two."
    ),
    docs_url="https://xcube.readthedocs.io/en/latest/mldatasets.html#definition",
)
class MLDatasetXY(RuleOp):
    def validate_dataset(self, ctx: RuleContext, node: DatasetNode):
        level_info = get_dataset_level_info(node.dataset)
        if level_info is None:
            # ok, this rules applies only to level datasets opened
            # by the xcube multi-level processor
            return

        level = level_info.level
        if level == 0:
            # ok, this rule does only apply to level > 0
            return

        datasets = level_info.datasets
        level_0_dataset, _ = datasets[0]
        l0_size = get_spatial_size(level_0_dataset)
        if l0_size is None:
            # ok, maybe no spatial data vars?
            return

        (x_name, level_0_width), (y_name, level_0_height) = l0_size
        level_width = node.dataset.sizes.get(x_name)
        level_height = node.dataset.sizes.get(y_name)
        expected_level_width = math.ceil(level_0_width >> level)
        expected_level_height = math.ceil(level_0_height >> level)

        if level_width != expected_level_width:
            ctx.report(
                f"Expected size of dimension {x_name!r} in level {level}"
                f" to be {expected_level_width}, but was {level_width}."
            )

        if level_height != expected_level_height:
            ctx.report(
                f"Expected size of dimension {y_name!r} in level {level}"
                f" to be {expected_level_height}, but was {level_height}."
            )

        # Here: check spatial coordinates...
