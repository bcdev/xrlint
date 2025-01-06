from xrlint.result import Suggestion
from xrlint.node import AttrsNode
from xrlint.plugins.core.rules import plugin
from xrlint.rule import RuleContext, RuleOp


@plugin.define_rule(
    "no-empty-attrs",
    version="1.0.0",
    type="suggestion",
    description="Every dataset element should have metadata that describes it.",
)
class NoEmptyAttrs(RuleOp):
    def attrs(self, ctx: RuleContext, node: AttrsNode):
        if not node.attrs:
            ctx.report(
                "Missing metadata, attributes are empty.",
                suggestions=[
                    Suggestion(
                        desc=(
                            "Make sure to add appropriate metadata"
                            " attributes to dataset elements."
                        )
                    )
                ],
            )
