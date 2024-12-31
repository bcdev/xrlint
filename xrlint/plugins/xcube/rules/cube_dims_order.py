from xrlint.node import DataArrayNode
from xrlint.plugins.xcube.rules import plugin
from xrlint.result import Suggestion
from xrlint.rule import RuleOp, RuleContext


@plugin.define_rule(
    "cube-dims-order",
    version="1.0.0",
    description=(
        "Order of dimensions in spatio-temporal datacube variables"
        " should be [time, ..., y, x]."
    ),
)
class CubeDimsOrder(RuleOp):
    def data_array(self, ctx: RuleContext, node: DataArrayNode):
        if node.in_data_vars():
            dims = list(node.data_array.dims)
            indexes = {d: i for i, d in enumerate(node.data_array.dims)}

            yx_names = None
            if "x" in indexes and "y" in indexes:
                yx_names = ["y", "x"]
            elif "lon" in indexes and "lat" in indexes:
                yx_names = ["lat", "lon"]
            else:
                # TODO: get yx_names/yx_indexes from grid-mapping
                pass
            if yx_names is None:
                # This rule only applies to spatial dimensions
                return

            t_name = None
            if "time" in indexes:
                t_name = "time"

            n = len(dims)
            t_index = indexes[t_name] if t_name else None
            y_index = indexes[yx_names[0]]
            x_index = indexes[yx_names[1]]

            yx_ok = y_index == n - 2 and x_index == n - 1
            t_ok = t_index is None or t_index == 0
            if not yx_ok or not t_ok:
                if t_index is None:
                    expected_dims = [d for d in dims if d not in yx_names] + yx_names
                else:
                    expected_dims = (
                        [t_name]
                        + [d for d in dims if d != t_name and d not in yx_names]
                        + yx_names
                    )
                # noinspection PyTypeChecker
                ctx.report(
                    f"order of dimensions should be"
                    f" {','.join(expected_dims)}, but was {','.join(dims)}",
                    suggestions=["Use xarray.transpose(...) to reorder dimensions."],
                )
