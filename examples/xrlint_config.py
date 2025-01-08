# XRLint configuration file example

from xrlint.config import Config
from xrlint.node import DatasetNode
from xrlint.plugin import Plugin
from xrlint.plugin import PluginMeta
from xrlint.rule import RuleContext
from xrlint.rule import RuleOp


plugin = Plugin(
    meta=PluginMeta(name="hello-plugin", version="1.0.0"),
    configs={
        "recommended": Config.from_value(
            {
                "rules": {
                    "hello/good-title": "error",
                },
            }
        )
    },
)


@plugin.define_rule(
    "good-title", description=f"Dataset title should be 'Hello World!'."
)
class GoodTitle(RuleOp):
    def dataset(self, ctx: RuleContext, node: DatasetNode):
        good_title = "Hello World!"
        if node.dataset.attrs.get("title") != good_title:
            ctx.report(
                "Attribute 'title' wrong.",
                suggestions=[f"Rename it to {good_title!r}."],
            )


def export_configs():
    return [
        {
            "files": ["**/*.zarr", "**/*.nc"],
        },
        {
            "plugins": {
                "hello": plugin,
            },
        },
        "recommended",
        "hello/recommended",
    ]
