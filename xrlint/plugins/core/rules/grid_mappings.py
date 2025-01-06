from xrlint.node import DatasetNode
from xrlint.plugins.core.rules import plugin
from xrlint.rule import RuleOp, RuleContext


@plugin.define_rule(
    "grid-mappings",
    version="1.0.0",
    type="problem",
    description=(
        "Grid mappings, if any, shall have valid grid mapping coordinate variables."
    ),
)
class GridMappings(RuleOp):
    def dataset(self, ctx: RuleContext, node: DatasetNode):
        dataset = node.dataset

        # Get the mapping of grid mapping names to grid-mapped variables
        grid_mapped_vars = {
            str(v.attrs.get("grid_mapping")): str(k)
            for k, v in dataset.data_vars.items()
            if "grid_mapping" in v.attrs
        }

        if len(grid_mapped_vars) == 0:
            return

        # Check validity of grid mappings
        for gm_name, var_name in grid_mapped_vars.items():
            gm_var = dataset.variables.get(gm_name)
            if gm_var is None:
                ctx.report(
                    f"Missing grid mapping variable {gm_name!r}"
                    f" referred to by variable {var_name!r}."
                )
            else:
                if gm_name not in dataset.coords:
                    ctx.report(
                        f"Grid mapping variable {gm_name!r} should"
                        f" be a coordinate variable, not data variable."
                    )
                if gm_var.dims:
                    dims_text = ",".join(str(d) for d in gm_var.dims)
                    ctx.report(
                        f"Grid mapping variable {gm_name!r} should be a scalar,"
                        f" but has dimension(s) {dims_text}."
                    )
                # Note: we could check if creating a CRS from
                #   gm_var.attrs is possible using pyproj.CRS.from_cf().
                #   Report otherwise.
                grid_mapping_name = gm_var.attrs.get("grid_mapping_name")
                if not grid_mapping_name:
                    ctx.report(
                        f"Grid mapping variable {gm_name!r} is missing"
                        f" a valid attribute 'grid_mapping_name'."
                    )
