from xrlint.node import DatasetNode
from xrlint.plugins.xcube.constants import LAT_NAME, LON_NAME
from xrlint.plugins.xcube.rules import plugin
from xrlint.rule import RuleOp, RuleContext

INVALID_LAT_NAMES = {"ltd", "latitude"}
INVALID_LON_NAMES = {"lng", "long", "longitude"}


@plugin.define_rule(
    "lat-lon-naming",
    version="1.0.0",
    type="problem",
    description=(
        f"Latitude and longitude coordinates and dimensions"
        f" should be called {LAT_NAME !r} and {LON_NAME !r}."
    ),
)
class LatLonNaming(RuleOp):
    def dataset(self, ctx: RuleContext, node: DatasetNode):
        lon_ok = _check(
            ctx, "variable", node.dataset.variables.keys(), INVALID_LON_NAMES, LON_NAME
        )
        lat_ok = _check(
            ctx, "variable", node.dataset.variables.keys(), INVALID_LAT_NAMES, LAT_NAME
        )
        if lon_ok and lat_ok:
            # If variables have been reported,
            # we should not need to report (their) coordinates
            _check(
                ctx,
                "dimension",
                node.dataset.sizes.keys(),
                INVALID_LON_NAMES,
                LON_NAME,
            )
            _check(
                ctx,
                "dimension",
                node.dataset.sizes.keys(),
                INVALID_LAT_NAMES,
                LAT_NAME,
            )


def _check(ctx, names_name, names, invalid_names, valid_name):
    names = [str(n) for n in names]  # xarray keys are Hashable, not str
    found_names = [
        n
        for n in names
        if (n.lower() in invalid_names) or (n.lower() == valid_name and n != valid_name)
    ]
    if found_names:
        ctx.report(
            f"The {names_name} {found_names[0]!r} should be named {valid_name!r}.",
            suggestions=[f"Rename {names_name} to {valid_name!r}."],
        )
        return False
    else:
        return True
