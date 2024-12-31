from xrlint.node import DatasetNode
from xrlint.plugins.xcube.rules import plugin
from xrlint.rule import RuleOp, RuleContext

VALID_LON = "lon"
VALID_LAT = "lat"
INVALID_LONS = {"lng", "long", "longitude"}
INVALID_LATS = {"ltd", "latitude"}


@plugin.define_rule(
    "lat-lon-naming",
    version="1.0.0",
    description=(
        f"Latitude and longitude coordinates and dimensions"
        f" should be called {VALID_LAT!r} and {VALID_LON!r}."
    ),
)
class LatLonNaming(RuleOp):
    def dataset(self, ctx: RuleContext, node: DatasetNode):
        lon_ok = _check(
            ctx, "variable", node.dataset.variables.keys(), INVALID_LONS, VALID_LON
        )
        lat_ok = _check(
            ctx, "variable", node.dataset.variables.keys(), INVALID_LATS, VALID_LAT
        )
        if lon_ok and lat_ok:
            # If variables have been reported,
            # we should not need to report (their) coordinates
            _check(ctx, "dimension", node.dataset.sizes.keys(), INVALID_LONS, VALID_LON)
            _check(ctx, "dimension", node.dataset.sizes.keys(), INVALID_LATS, VALID_LAT)


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
