"""
This configuration example shows how to define and use a plugin
using the `Plugin` class and its `define_rule()` decorator method.
"""

#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from xrlint.node import DatasetNode
from xrlint.plugin import new_plugin
from xrlint.rule import RuleContext, RuleOp

plugin = new_plugin(name="hello-plugin", version="1.0.0")


@plugin.define_rule("good-title")
class GoodTitle(RuleOp):
    """Dataset title should be 'Hello World!'."""

    def validate_dataset(self, ctx: RuleContext, node: DatasetNode):
        good_title = "Hello World!"
        if node.dataset.attrs.get("title") != good_title:
            ctx.report(
                "Attribute 'title' wrong.",
                suggestions=[f"Rename it to {good_title!r}."],
            )


# Define more rules here...


plugin.define_config(
    "recommended",
    [
        {
            "rules": {
                "hello/good-title": "warn",
                # Configure more rules here...
            },
        }
    ],
)

# Add more configurations here...


def export_config():
    return [
        # Use "hello" plugin
        {
            "plugins": {
                "hello": plugin,
            },
        },
        # Use recommended settings from xrlint
        "recommended",
        # Use recommended settings from "hello" plugin
        "hello/recommended",
    ]
