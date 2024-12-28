import xrlint.api as xrl
from xrlint.plugins.core.rules import registry


@registry.define_rule(name="dataset-title-attr", version="1.0.0")
class DatasetTitleAttr(xrl.RuleOp):
    def dataset(self, ctx: xrl.RuleContext, node: xrl.DatasetNode):
        title = node.dataset.attrs.get("title")
        if not title:
            ctx.report("Missing 'title' attribute in dataset.")
