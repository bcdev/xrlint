import xrlint.api as xrl
from xrlint.plugins.xcube.rules import plugin


@plugin.define_rule("spatial-dims-order")
class SpatialDimsOrder(xrl.RuleOp):
    def data_array(self, ctx: xrl.RuleContext, node: xrl.DataArrayNode):
        if node.in_data_vars():
            dims = list(node.data_array.dims)
            try:
                yx_names = ["y", "x"]
                yx_indexes = tuple(map(dims.index, yx_names))
            except ValueError:
                try:
                    yx_names = ["lat", "lon"]
                    yx_indexes = tuple(map(dims.index, yx_names))
                except ValueError:
                    return
            n = len(dims)
            y_index, x_index = yx_indexes
            if y_index != n - 2 or x_index != n - 1:
                expected_dims = [d for d in dims if d not in yx_names] + yx_names
                # noinspection PyTypeChecker
                ctx.report(
                    f"order of dimensions should be"
                    f" {','.join(expected_dims)}, but was {','.join(dims)}"
                )
