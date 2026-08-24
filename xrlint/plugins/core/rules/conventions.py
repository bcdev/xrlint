#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

import re

from xrlint.node import DatasetNode
from xrlint.plugins.core.plugin import plugin
from xrlint.util.attrs import hierarchical_attrs
from xrlint.rule import RuleContext, RuleExit, RuleOp
from xrlint.util.schema import schema


@plugin.define_rule(
    "conventions",
    version="1.0.0",
    type="suggestion",
    description=(
        "Datasets should identify the applicable conventions"
        " using the `Conventions` attribute.\n"
        " The rule has an optional configuration parameter `match` which"
        " is a regex pattern that the value of the `Conventions` attribute"
        " must match, if any. If not provided, the rule just verifies"
        " that the attribute exists and whether it is a character string."
        " For `xarray.DataTree` inputs, the attribute may be defined on"
        " a parent group; local dataset attributes take precedence over"
        " parent attributes."
    ),
    docs_url=(
        "https://cfconventions.org/cf-conventions/cf-conventions.html"
        "#identification-of-conventions"
    ),
    schema=schema(
        "object",
        properties={
            "match": schema("string", title="Regex pattern"),
        },
    ),
)
class Conventions(RuleOp):
    def __init__(self, match: str | None = None):
        self.match = re.compile(match) if match else None

    def validate_dataset(self, ctx: RuleContext, node: DatasetNode):
        attrs = hierarchical_attrs(node)
        if "Conventions" not in attrs:
            ctx.report("Missing attribute 'Conventions'.")
        else:
            value = attrs.get("Conventions")
            if not isinstance(value, str) and value:
                ctx.report(f"Invalid attribute 'Conventions': {value!r}.")
            elif self.match is not None and not self.match.match(value):
                ctx.report(
                    f"Invalid attribute 'Conventions':"
                    f" {value!r} doesn't match {self.match.pattern!r}."
                )
        raise RuleExit
