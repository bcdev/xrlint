import re


from xrlint.node import DatasetNode
from xrlint.plugins.core.plugin import plugin
from xrlint.rule import RuleContext, RuleOp, RuleExit
from xrlint.util.schema import schema

DEFAULT_ATTR_NAMES = ["Conventions", "title", "source", "history", "name"]


@plugin.define_rule(
    "conventions",
    version="1.0.0",
    type="suggestion",
    description=(
        "Datasets should identify the applicable conventions"
        " using the `Conventions` attribute.\n"
        " The rule has an optional configuration parameter `match` which"
        " is a regex pattern that the value of the `Conventions` attribute"
        " must match, if any."
    ),
    docs_url=(
        "https://cfconventions.org/cf-conventions/cf-conventions.html"
        "#identification-of-conventions"
    ),
    schema=schema(
        "object", properties=dict(match=schema("string", title="Regex pattern"))
    ),
)
class Conventions(RuleOp):
    def __init__(self, match: str | None = None):
        self.match = re.compile(match) if match else None

    def dataset(self, ctx: RuleContext, node: DatasetNode):
        if "Conventions" not in node.dataset.attrs:
            ctx.report("Missing attribute 'Conventions'.")
        else:
            conventions_spec = node.dataset.attrs.get("Conventions")
            if not isinstance(conventions_spec, str):
                ctx.report(
                    f"Invalid attribute 'Conventions':"
                    f" expected string, got value {conventions_spec!r}."
                )
            elif self.match is not None and not self.match.match(conventions_spec):
                ctx.report(
                    f"Invalid attribute 'Conventions':"
                    f" {conventions_spec!r} doesn't match pattern {self.match.pattern!r}."
                )
        raise RuleExit
