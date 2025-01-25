from xrlint.node import DataArrayNode
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
    def dataset(self, ctx: RuleContext, node: DataArrayNode):
        source = ctx.dataset.encoding.get("source")
        is_zarr = isinstance(source, str) and source.endswith(".zarr")
        if not is_zarr:
            # if not a Zarr, no need to check further
            raise RuleExit

    def data_array(self, ctx: RuleContext, node: DataArrayNode):
        if (
            "write_empty_chunks" not in node.data_array.encoding
            and "chunks" in node.data_array.encoding
            and "_FillValue" in node.data_array.encoding
        ):
            ctx.report("Consider writing the dataset using 'write_empty_chunks=True'.")
