from xrlint.node import DatasetNode
from xrlint.plugins.xcube.constants import ML_META_FILENAME
from xrlint.plugins.xcube.plugin import plugin
from xrlint.plugins.xcube.util import get_dataset_level_info, is_spatial_var
from xrlint.rule import RuleContext, RuleOp
from xrlint.util.formatting import format_item


@plugin.define_rule(
    "ml-dataset-meta",
    version="1.0.0",
    type="suggestion",
    description=(
        f"Multi-level datasets should provide {ML_META_FILENAME!r}"
        f" meta information file and if so, it should be consistent."
    ),
    docs_url=(
        "https://xcube.readthedocs.io/en/latest/mldatasets.html#the-xcube-levels-format"
    ),
)
class MLDatasetMeta(RuleOp):
    def dataset(self, ctx: RuleContext, node: DatasetNode):
        level_info = get_dataset_level_info(node.dataset)
        if level_info is None:
            # ok, this rules applies only to level datasets opened
            # by the xcube multi-level processor
            return

        level = level_info.level
        if level > 0:
            # ok, this rule does only apply to level 0
            return

        meta = level_info.meta
        if meta is None:
            ctx.report(
                f"Missing {ML_META_FILENAME!r} meta-info file,"
                f" therefore dataset cannot be extended."
            )
            return

        if not meta.version.startswith("1."):
            ctx.report(f"Unsupported {ML_META_FILENAME!r} meta-info version.")

        if meta.num_levels <= 0:
            ctx.report(
                f"Invalid 'num_levels' in {ML_META_FILENAME!r} meta-info:"
                f" {meta.num_levels}."
            )
        elif meta.num_levels != level_info.num_levels:
            ctx.report(
                f"Expected {format_item(meta.num_levels, 'level')},"
                f" but found {level_info.num_levels}."
            )

        if meta.use_saved_levels is None:
            ctx.report(
                f"Missing value for 'use_saved_levels'"
                f" in {ML_META_FILENAME!r} meta-info."
            )

        if not meta.agg_methods:
            ctx.report(
                f"Missing value for 'agg_methods' in {ML_META_FILENAME!r} meta-info."
            )
        else:
            for var_name, var in node.dataset.data_vars.items():
                if is_spatial_var(var) and not meta.agg_methods.get(var_name):
                    ctx.report(
                        f"Missing value for variable {var_name!r}"
                        f" in 'agg_methods' of {ML_META_FILENAME!r} meta-info."
                    )
            for var_name in meta.agg_methods.keys():
                if var_name not in node.dataset:
                    ctx.report(
                        f"Variable {var_name!r} not found in dataset, but specified"
                        f" in 'agg_methods' of {ML_META_FILENAME!r} meta-info."
                    )

        # Later: check meta.tile_size as well...
