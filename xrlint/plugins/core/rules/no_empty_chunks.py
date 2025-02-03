#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from xrlint.node import DatasetNode
from xrlint.plugins.core.plugin import plugin
from xrlint.rule import RuleContext, RuleExit, RuleOp


@plugin.define_rule(
    "no-empty-chunks",
    version="1.0.0",
    type="suggestion",
    description=(
        "Empty chunks should not be encoded and written."
        " The rule currently applies to Zarr format only."
    ),
    docs_url=(
        "https://docs.xarray.dev/en/stable/generated/xarray.Dataset.to_zarr.html"
        "#xarray-dataset-to-zarr"
    ),
)
class NoEmptyChunks(RuleOp):
    def validate_dataset(self, ctx: RuleContext, node: DatasetNode):
        source = node.dataset.encoding.get("source")
        is_zarr = isinstance(source, str) and source.endswith(".zarr")
        if is_zarr:
            for var in node.dataset.data_vars.values():
                is_chunked_in_storage = (
                    "_FillValue" in var.encoding
                    and "chunks" in var.encoding
                    and tuple(var.encoding.get("chunks")) != tuple(var.shape)
                )
                if is_chunked_in_storage:
                    ctx.report("Consider writing with `write_empty_chunks=False`.")
                    break
        # no need to traverse further
        raise RuleExit
