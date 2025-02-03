#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from collections.abc import Hashable
from typing import Any

import xarray as xr

from xrlint.node import DatasetNode
from xrlint.plugins.xcube.constants import TIME_NAME
from xrlint.plugins.xcube.plugin import plugin
from xrlint.rule import RuleContext, RuleOp


@plugin.define_rule(
    "time-naming",
    version="1.0.0",
    type="problem",
    description=f"Time coordinate and dimension should be called {TIME_NAME!r}.",
    docs_url="https://xcube.readthedocs.io/en/latest/cubespec.html#temporal-reference",
)
class TimeNaming(RuleOp):
    def validate_dataset(self, ctx: RuleContext, node: DatasetNode):
        time_vars = {
            var_name: var
            for var_name, var in node.dataset.coords.items()
            if var_name != TIME_NAME and _is_time_coord(var_name, var)
        }
        for var_name, var in time_vars.items():
            ctx.report(
                f"The coordinate {var_name!r} should be named {TIME_NAME!r}.",
                suggestions=[f"Rename {var_name!r} to {TIME_NAME!r}."],
            )

        time_var = node.dataset.coords.get(TIME_NAME)
        if time_var is not None:
            if not _is_time_coord(TIME_NAME, time_var):
                ctx.report(f"Missing time units for coordinate {TIME_NAME!r}.")
            if not _get_time_encoding_attr(time_var, "calendar"):
                ctx.report(f"Missing calendar for coordinate {TIME_NAME!r}.")


def _is_time_coord(var_name: Hashable, var: xr.DataArray) -> bool:
    if var.dims == (var_name,):
        units = _get_time_encoding_attr(var, "units")
        return units and " since " in units
    return False


def _get_time_encoding_attr(var: xr.DataArray, name: str) -> Any:
    # decode_cf=True / decode_cf=False
    return var.encoding.get(name, var.attrs.get(name))
