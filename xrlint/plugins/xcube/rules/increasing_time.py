import numpy as np

from xrlint.node import DataArrayNode
from xrlint.plugins.xcube.rules import plugin
from xrlint.rule import RuleContext
from xrlint.rule import RuleExit
from xrlint.rule import RuleOp
from xrlint.util.formatting import format_count
from xrlint.util.formatting import format_seq


@plugin.define_rule(
    "increasing-time",
    version="1.0.0",
    type="problem",
    description="Time coordinate labels should be monotonically increasing.",
)
class IncreasingTime(RuleOp):
    def data_array(self, ctx: RuleContext, node: DataArrayNode):
        array = node.data_array
        if node.in_coords() and node.name == "time" and array.dims == ("time",):
            diff_array: np.ndarray = array.diff("time").values
            if not np.count_nonzero(diff_array > 0) == diff_array.size:
                check_indexes(ctx, diff_array == 0, "Duplicate")
                check_indexes(ctx, diff_array < 0, "Backsliding")
                raise RuleExit  # No need to apply rule any further


def check_indexes(ctx, cond: np.ndarray, issue_name: str):
    (indexes,) = np.nonzero(cond)
    if indexes.size > 0:
        index_text = format_count(indexes.size, singular="index", plural="indexes")
        ctx.report(
            f"{issue_name} 'time' coordinate label at {index_text}"
            f" {format_seq(indexes)}"
        )
