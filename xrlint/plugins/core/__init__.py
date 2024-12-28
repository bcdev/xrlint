from xrlint.config import Config
from xrlint.plugin import Plugin
from xrlint.util.importutil import import_submodules


def plugin() -> Plugin:
    from .rules import plugin

    import_submodules("xrlint.plugins.core.rules")

    plugin.configs["recommended"] = Config.from_value(
        {
            "name": "recommended",
            "rules": {f"{rule_id}": "error" for rule_id, rule in plugin.rules.items()},
        }
    )

    return plugin
