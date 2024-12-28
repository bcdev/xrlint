from xrlint.node import DatasetNode
from xrlint.plugins.core.rules import plugin
from xrlint.rule import RuleContext, RuleOp


@plugin.define_rule("dataset-title-attr", version="1.0.0")
class DatasetTitleAttr(RuleOp):
    def dataset(self, ctx: RuleContext, node: DatasetNode):
        title = node.dataset.attrs.get("title")
        if not title:
            ctx.report("Missing 'title' attribute in dataset.")