from xrlint.config import Config
from xrlint.plugin import Plugin
from xrlint.util.importutil import import_submodules


def export_plugin() -> Plugin:
    from .rules import plugin

    import_submodules("xrlint.plugins.xcube.rules")

    plugin.configs["xcube-recommended"] = Config.from_value(
        {
            "name": "xcube-recommended",
            "rules": {f"{rule_id}": "error" for rule_id, rule in plugin.rules.items()},
        }
    )

    return plugin
