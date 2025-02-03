#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from typing import Final

from xrlint.node import DatasetNode
from xrlint.plugins.core.plugin import plugin
from xrlint.rule import RuleContext, RuleExit, RuleOp
from xrlint.util.formatting import format_count
from xrlint.util.schema import schema

DEFAULT_THRESHOLD: Final = 2.5  # seconds


@plugin.define_rule(
    "access-latency",
    version="1.0.0",
    description=(
        "Ensure that the time it takes to open a dataset from its source"
        " does a exceed a given `threshold` in seconds."
        f" The default threshold is `{DEFAULT_THRESHOLD}`."
    ),
    schema=schema(
        "object",
        properties={
            "threshold": schema(
                "number",
                exclusiveMinimum=0,
                default=DEFAULT_THRESHOLD,
                title="Threshold time in seconds",
            )
        },
    ),
)
class AccessLatency(RuleOp):
    def __init__(self, threshold: float = DEFAULT_THRESHOLD):
        self.threshold = threshold

    def validate_dataset(self, ctx: RuleContext, node: DatasetNode) -> None:
        if ctx.access_latency is not None and ctx.access_latency > self.threshold:
            ctx.report(
                f"Access latency exceeds threshold: {ctx.access_latency:.1f}"
                f" > {format_count(self.threshold, 'second')}."
            )
        raise RuleExit
