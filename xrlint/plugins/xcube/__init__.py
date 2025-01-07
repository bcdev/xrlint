from xrlint.config import Config
from xrlint.plugin import Plugin
from xrlint.util.importutil import import_submodules


def export_plugin() -> Plugin:
    from .rules import plugin

    import_submodules("xrlint.plugins.xcube.rules")

    plugin.configs["recommended"] = Config.from_value(
        {
            "name": "xcube-recommended",
            "plugins": {
                "xcube": plugin,
            },
            "rules": {
                "xcube/any-spatial-data-var": "error",
                "xcube/cube-dims-order": "error",
                "xcube/data-var-colors": "warn",
                "xcube/grid-mapping-naming": "warn",
                "xcube/increasing-time": "error",
                "xcube/lat-lon-naming": "error",
                "xcube/single-grid-mapping": "error",
            },
        }
    )
    plugin.configs["all"] = Config.from_value(
        {
            "name": "xcube-all",
            "plugins": {
                "xcube": plugin,
            },
            "rules": {f"xcube/{rule_id}": "error" for rule_id in plugin.rules.keys()},
        }
    )

    return plugin
