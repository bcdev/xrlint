from xrlint.node import DatasetNode
from xrlint.plugins.xcube.constants import ML_META_FILENAME
from xrlint.plugins.xcube.plugin import plugin
from xrlint.plugins.xcube.util import get_dataset_level_info
from xrlint.rule import RuleContext, RuleOp
from xrlint.util.formatting import format_item


@plugin.define_rule(
    "ml-dataset-meta",
    version="1.0.0",
    type="suggestion",
    description=(
        f"Multi-level datasets should provide {ML_META_FILENAME!r} meta information file"
        f" and if so, it should be consistent."
    ),
    docs_url=(
        "https://xcube.readthedocs.io/en/latest/cubespec.html#encoding-of-colors"
    ),
)
class MultiLevelDatasetMeta(RuleOp):
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
                f"Missing {ML_META_FILENAME!r} file,"
                f" therefore dataset cannot be extended."
            )
            return

        actual_count: int = level_info.num_levels
        meta_count = meta.num_levels
        if meta_count != actual_count:
            ctx.report(
                f"Expected {format_item(meta_count, 'level')}, but found {actual_count}"
            )

        actual_count: int = level_info.num_levels
        meta_count = meta.use_saved_levels
        if meta_count != actual_count:
            ctx.report(
                f"Expected {format_item(meta_count, 'level')}, but found {actual_count}"
            )

        # TODO: verify variables listed in meta
