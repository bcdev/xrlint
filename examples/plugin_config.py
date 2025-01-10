"""
This configuration example shows how to define and use a plugin
using the `Plugin` class and its `define_rule()` decorator method.
"""

from xrlint.config import Config
from xrlint.node import DatasetNode
from xrlint.plugin import Plugin
from xrlint.plugin import PluginMeta
from xrlint.rule import RuleContext
from xrlint.rule import RuleOp


plugin = Plugin(
    meta=PluginMeta(name="hello-plugin", version="1.0.0"),
    configs={
        # "configs" entries must be `Config` objects!
        "recommended": Config.from_value(
            {
                "rules": {
                    "hello/good-title": "warn",
                    # Configure more rules here...
                },
            }
        ),
        # Add more configurations here...
    },
)


@plugin.define_rule("good-title")
class GoodTitle(RuleOp):
    """Dataset title should be 'Hello World!'."""

    def dataset(self, ctx: RuleContext, node: DatasetNode):
        good_title = "Hello World!"
        if node.dataset.attrs.get("title") != good_title:
            ctx.report(
                "Attribute 'title' wrong.",
                suggestions=[f"Rename it to {good_title!r}."],
            )


# Define more rules here...


def export_configs():
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
