from xrlint.node import DatasetNode
from xrlint.plugins.xcube.constants import LAT_NAME, LON_NAME, GM_NAMES_TEXT
from xrlint.plugins.xcube.rules import plugin
from xrlint.plugins.xcube.util import is_spatial_var
from xrlint.rule import RuleOp, RuleContext


@plugin.define_rule(
    "single-grid-mapping",
    version="1.0.0",
    type="problem",
    description=(
        "A single grid mapping shall be used for all"
        " spatial data variables of a datacube."
    ),
)
class SingleGridMapping(RuleOp):
    def dataset(self, ctx: RuleContext, node: DatasetNode):
        dataset = node.dataset

        if not dataset.data_vars:
            # Rule applies to dataset with data variables only
            return

        # Get the mapping of grid mapping names to grid-mapped variables
        grid_mapped_vars = {
            str(v.attrs.get("grid_mapping")): str(k)
            for k, v in dataset.data_vars.items()
            if (is_spatial_var(v)) and "grid_mapping" in v.attrs
        }

        # datacubes with geographic CRS do not need an explicit grid mapping
        geo_crs = LON_NAME in dataset.coords and LAT_NAME in dataset.coords
        if geo_crs and not grid_mapped_vars:
            return

        # if there is not a single grid mapping then report it
        if len(grid_mapped_vars) > 1:
            gm_names = "".join(
                [
                    f"var {var_name!r} -> {gm_name!r}"
                    for gm_name, var_name in grid_mapped_vars.items()
                ]
            )
            ctx.report(
                f"Spatial variables refer to multiple grid mappings: {gm_names}.",
                suggestions=[
                    (
                        "Split datacube into multiple datacubes"
                        " each with a single grid mapping."
                    ),
                ],
            )
        elif len(grid_mapped_vars) == 0:
            ctx.report(
                "None of the spatial variables provides a grid mapping.",
                suggestions=[
                    (
                        f"Add a grid mapping coordinate variable named"
                        f" {GM_NAMES_TEXT} to the dataset."
                    ),
                    (
                        "Set attribute 'grid_mapping' of spatial data variables"
                        " to the name of the grid mapping coordinate variable."
                    ),
                ],
            )

        # Note the validity of grid mappings should be covered by
        # core rule "grid-mappings".
