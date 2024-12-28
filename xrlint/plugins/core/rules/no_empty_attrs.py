import xrlint.api as xrl
from xrlint.plugins.core.rules import plugin


@plugin.define_rule("no-empty-attrs", version="1.0.0")
class NoEmptyAttrs(xrl.RuleOp):
    def attrs(self, ctx: xrl.RuleContext, node: xrl.AttrsNode):
        if not node.attrs:
            ctx.report(
                "Attributes are empty.",
                suggestions=[
                    xrl.Suggestion(
                        desc="Make sure to add appropriate metadata to dataset nodes."
                    )
                ],
            )
