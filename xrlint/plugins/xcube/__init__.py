from xrlint.config import Config
from xrlint.plugin import Plugin
from xrlint.util.importutil import import_submodules


def export_plugin() -> Plugin:
    from .rules import plugin

    import_submodules("xrlint.plugins.xcube.rules")

    plugin.configs["recommended"] = Config.from_value(
        {
            "name": "recommended",
            "rules": {
                "xcube/cube-dims-order": "error",
            },
        }
    )

    return plugin
