from xrlint.message import Suggestion
from xrlint.node import AttrsNode
from xrlint.rule import RuleContext, RuleOp
from xrlint.plugins.core.rules import plugin


@plugin.define_rule("no-empty-attrs", version="1.0.0")
class NoEmptyAttrs(RuleOp):
    def attrs(self, ctx: RuleContext, node: AttrsNode):
        if not node.attrs:
            ctx.report(
                "Attributes are empty.",
                suggestions=[
                    Suggestion(
                        desc="Make sure to add appropriate metadata to dataset nodes."
                    )
                ],
            )
