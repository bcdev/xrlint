#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

import numpy as np

from xrlint.node import VariableNode
from xrlint.plugins.core.plugin import plugin
from xrlint.rule import RuleContext, RuleOp


@plugin.define_rule(
    "var-missing-data",
    version="1.0.0",
    type="suggestion",
    description=(
        "Checks the recommended use of missing data, i.e., coordinate variables"
        " should not define missing data, but packed data should."
        " Notifies about the use of valid ranges to indicate missing data, which"
        " is currently not supported by xarray."
    ),
    docs_url="https://cfconventions.org/cf-conventions/cf-conventions.html#units",
)
class VarMissingData(RuleOp):
    def validate_variable(self, ctx: RuleContext, node: VariableNode):
        array = node.array
        encoding = array.encoding
        attrs = array.attrs

        fill_value_source = None
        if "_FillValue" in encoding:
            fill_value_source = "encoding"
        elif "_FillValue" in attrs:
            fill_value_source = "attribute"

        if fill_value_source is not None and node.name in ctx.dataset.coords:
            ctx.report(
                f"Unexpected {fill_value_source} '_FillValue',"
                f" coordinates must not have missing data."
            )
        elif fill_value_source is None and node.name in ctx.dataset.data_vars:
            scaling_factor = encoding.get("scaling_factor", attrs.get("scaling_factor"))
            add_offset = encoding.get("add_offset", attrs.get("add_offset"))
            raw_dtype = encoding.get("dtype")
            if add_offset is not None or scaling_factor is not None:
                ctx.report("Missing attribute '_FillValue' since data packing is used.")
            elif isinstance(raw_dtype, np.dtype) and np.issubdtype(
                raw_dtype, np.floating
            ):
                ctx.report("Missing attribute '_FillValue', which should be NaN.")

        if any((name in attrs) for name in ("valid_min", "valid_max", "valid_range")):
            ctx.report("Valid ranges are not recognized by xarray (as of Feb 2025).")
