from xrlint.config import Config
from xrlint.plugin import Plugin
from xrlint.util.importutil import import_submodules


def export_plugin() -> Plugin:
    from .rules import plugin

    import_submodules("xrlint.plugins.core.rules")

    plugin.configs["recommended"] = Config.from_value(
        {
            "name": "recommended",
            "rules": {
                "coords-for-dims": "error",
                "dataset-title-attr": "warn",
                "grid-mappings": "error",
                "no-empty-attrs": "warn",
                "var-units-attr": "warn",
            },
        }
    )
    plugin.configs["all"] = Config.from_value(
        {
            "name": "all",
            "rules": {rule_id: "error" for rule_id in plugin.rules.keys()},
        }
    )

    return plugin
