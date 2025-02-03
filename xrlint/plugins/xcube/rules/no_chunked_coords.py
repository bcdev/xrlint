#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

import math

from xrlint.node import VariableNode
from xrlint.plugins.xcube.plugin import plugin
from xrlint.rule import RuleContext, RuleOp
from xrlint.util.schema import schema

DEFAULT_LIMIT = 5


@plugin.define_rule(
    "no-chunked-coords",
    version="1.0.0",
    type="problem",
    description=(
        "Coordinate variables should not be chunked."
        " Can be used to identify performance issues, where chunked coordinates"
        " can cause slow opening if datasets due to the many chunk-fetching"
        " requests made to (remote) filesystems with low bandwidth."
        " You can use the `limit` parameter to specify an acceptable number "
        f" of chunks. Its default is {DEFAULT_LIMIT}."
    ),
    schema=schema(
        "object",
        properties=dict(
            limit=schema(
                "integer",
                minimum=0,
                default=DEFAULT_LIMIT,
                title="Acceptable number of chunks",
            )
        ),
    ),
)
class NoChunkedCoords(RuleOp):
    def __init__(self, limit: int = DEFAULT_LIMIT):
        self.limit = limit

    def validate_variable(self, ctx: RuleContext, node: VariableNode):
        if node.name not in ctx.dataset.coords or node.array.ndim != 1:
            return

        chunks = node.array.encoding.get("chunks")
        if isinstance(chunks, (list, tuple)) and len(chunks) == 1:
            num_chunks = math.ceil(node.array.size / chunks[0])
            if num_chunks > self.limit:
                ctx.report(
                    f"Number of chunks exceeds limit: {num_chunks} > {self.limit}.",
                    suggestions=["Combine chunks into a one or more larger ones."],
                )
