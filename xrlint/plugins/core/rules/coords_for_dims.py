from xrlint.node import DatasetNode
from xrlint.plugins.core.rules import plugin
from xrlint.rule import RuleContext, RuleOp
from xrlint.util.formatting import format_item


@plugin.define_rule(
    "coords-for-dims",
    version="1.0.0",
    type="problem",
    description="Dimensions of data variables should have corresponding coordinates.",
)
class CoordsForDims(RuleOp):
    def dataset(self, ctx: RuleContext, node: DatasetNode):
        dataset = node.dataset

        # Get data variable dimensions
        data_var_dims = set()
        for v in dataset.data_vars.values():
            data_var_dims.update(v.dims)
        if not data_var_dims:
            return

        # Get dimensions with coordinate variables
        no_coord_dims = []
        for d in sorted(str(d) for d in data_var_dims):
            if d not in dataset.coords:
                no_coord_dims.append(d)

        if no_coord_dims:
            n = len(no_coord_dims)
            ctx.report(
                f"{format_item(n, 'Data variable dimension')} without"
                f" coordinates: {', '.join(no_coord_dims)}",
                suggestions=[
                    f"Add corresponding {format_item(n, 'coordinate variable')}"
                    f" to dataset:"
                    f" {', '.join(f'{d}[{dataset.sizes[d]}]' for d in no_coord_dims)}."
                ],
            )
