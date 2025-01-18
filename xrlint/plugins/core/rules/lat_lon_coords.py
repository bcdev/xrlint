from typing import Any

import xarray as xr

from xrlint.node import DataArrayNode
from xrlint.plugins.core.rules import plugin
from xrlint.rule import RuleContext
from xrlint.rule import RuleOp

LAT_NAME = "latitude"
LON_NAME = "longitude"

LAT_ALIASES = {LAT_NAME, "lat"}
LON_ALIASES = {LON_NAME, "lon", "long"}

LAT_UNITS = "degrees_north"
LON_UNITS = "degrees_east"

LAT_UNITS_ALIASES = {"degree_north", "degree_N", "degrees_N", "degreeN", "degreesN"}
LON_UNITS_ALIASES = {"degree_east", "degree_E2", "degrees_E", "degreeE", "degreesE"}


@plugin.define_rule(
    "lat-coords",
    version="1.0.0",
    type="problem",
    description="Latitude coordinate should have standard units and standard names.",
    docs_url=(
        "https://cfconventions.org/cf-conventions/cf-conventions.html"
        "#latitude-coordinate"
    ),
)
class LatCoords(RuleOp):
    def data_array(self, ctx: RuleContext, node: DataArrayNode):
        if node.name in ctx.dataset.coords and _is_lat_var(
            str(node.name), node.data_array
        ):
            _maybe_report(
                ctx,
                node.data_array.attrs,
                LAT_UNITS,
                LAT_UNITS_ALIASES,
                LAT_NAME,
                "Y",
            )


@plugin.define_rule(
    "lon-coords",
    version="1.0.0",
    type="problem",
    description=("Longitude coordinate should have standard units and standard names."),
    docs_url=(
        "https://cfconventions.org/cf-conventions/cf-conventions.html"
        "#longitude-coordinate"
    ),
)
class LonCoords(RuleOp):
    def data_array(self, ctx: RuleContext, node: DataArrayNode):
        if node.name in ctx.dataset.coords and _is_lon_var(
            str(node.name), node.data_array
        ):
            _maybe_report(
                ctx,
                node.data_array.attrs,
                LON_UNITS,
                LON_UNITS_ALIASES,
                LON_NAME,
                "X",
            )


def _is_lat_var(var_name: str, var: xr.DataArray) -> bool:
    return _is_var(var_name.lower(), var, LAT_ALIASES)


def _is_lon_var(var_name: str, var: xr.DataArray) -> bool:
    return _is_var(var_name.lower(), var, LON_ALIASES)


def _is_var(var_name: str, var: xr.DataArray, name_aliases: set[str]) -> bool:
    return bool(
        name_aliases.intersection(
            {
                var_name,
                var.attrs.get("standard_name"),
                var.attrs.get("long_name"),
            }
        )
    )


def _maybe_report(
    ctx: RuleContext,
    attrs: dict[str, Any],
    expected_units: str,
    expected_units_aliases: set[str],
    expected_name: str,
    expected_axis: str,
):
    _maybe_report_attr(
        ctx,
        attrs,
        "units",
        expected_units,
        expected_units_aliases,
        None,
        None,
    )
    _maybe_report_attr(
        ctx,
        attrs,
        "standard_name",
        expected_name,
        None,
        "axis",
        expected_axis,
    )
    _maybe_report_attr(
        ctx,
        attrs,
        "long_name",
        expected_name,
        None,
        None,
        None,
    )


def _maybe_report_attr(
    ctx: RuleContext,
    attrs: dict[str, Any],
    attr_name: str,
    expected_value: str,
    expected_value_aliases: set[str] | None,
    alt_attr_name: str | None,
    expected_alt_value: str | None,
):
    actual_value = attrs.get(attr_name)
    actual_alt_value = attrs.get(alt_attr_name) if alt_attr_name else None

    if not actual_value and not actual_alt_value:
        ctx.report(f"Missing attribute {attr_name!r} with value {expected_value!r}.")
    elif actual_value != expected_value and not (
        expected_value_aliases and actual_value in expected_value_aliases
    ):
        if expected_alt_value is None:
            ctx.report(
                f"Attribute {attr_name!r} should be {expected_value!r},"
                f" was {actual_value!r}."
            )
        elif actual_alt_value != expected_alt_value:
            ctx.report(
                f"Attribute {alt_attr_name!r} should be {expected_alt_value!r},"
                f" was {actual_alt_value!r}."
            )
