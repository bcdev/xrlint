CONFIG_EXTENSIONS = ".yml", ".yaml", ".json", ".py"

DEFAULT_CONFIG_BASENAME = "xrlint.config"
DEFAULT_CONFIG_FILENAMES = [
    f"{DEFAULT_CONFIG_BASENAME}.py",
    f"{DEFAULT_CONFIG_BASENAME}.yaml",
    f"{DEFAULT_CONFIG_BASENAME}.json",
]

DEFAULT_OUTPUT_FORMAT = "simple"
DEFAULT_MAX_WARNINGS = 5

INIT_CONFIG_FILENAME = f"{DEFAULT_CONFIG_BASENAME}.py"
INIT_CONFIG_PY = """# XRLint configuration template
from xrlint.config import Config
from xrlint.rule import RuleContext
from xrlint.rule import RuleOp
from xrlint.plugin import Plugin
from xrlint.plugin import PluginMeta
from xrlint.node import DatasetNode


GOOD_TITLE = "Hello World!"

plugin = Plugin(meta=PluginMeta(name="hello-plugin", version="1.0.0"))


@plugin.define_rule(
    "good-title", description=f"Dataset title should be {GOOD_TITLE!r}."
)
class TitleHello(RuleOp):
    def dataset(self, ctx: RuleContext, node: DatasetNode):
        if node.dataset.attrs.get("title") != GOOD_TITLE:
            ctx.report(
                "Attribute 'title' wrong.",
                suggestions=[f"Rename it to {GOOD_TITLE!r}."],
            )


plugin.configs["recommended"] = Config.from_value(
    {
        "rules": {
            "hello/good-title": "error",
        },
    }
)


def export_configs():
    return
        {
            "files": ["**/*.zarr", "**/*.nc"],
        },
        {
            "plugins": {
                "hello": plugin,
            },
        },
        plugin.configs["recommended"],
    ]
"""
