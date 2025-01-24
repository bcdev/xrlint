from xrlint.plugin import Plugin
from xrlint.util.importutil import import_submodules


def export_plugin() -> Plugin:
    from .plugin import plugin

    import_submodules("xrlint.plugins.core.rules")

    plugin.define_config(
        "recommended",
        {
            "name": "recommended",
            "rules": {
                "coords-for-dims": "error",
                "dataset-title-attr": "warn",
                "flags": "error",
                "grid-mappings": "error",
                "lat-coordinate": "error",
                "lon-coordinate": "error",
                "no-empty-attrs": "warn",
                "no-empty-chunks": "warn",
                "time-coordinate": "error",
                "var-units-attr": "warn",
            },
        },
    )

    plugin.define_config(
        "all",
        {
            "name": "all",
            "rules": {rule_id: "error" for rule_id in plugin.rules.keys()},
        },
    )

    return plugin
