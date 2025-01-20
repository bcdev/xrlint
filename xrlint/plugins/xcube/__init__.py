from xrlint.config import Config
from xrlint.plugin import Plugin
from xrlint.util.importutil import import_submodules


def export_plugin() -> Plugin:
    from .plugin import plugin

    import_submodules("xrlint.plugins.xcube.rules")
    import_submodules("xrlint.plugins.xcube.processors")

    plugin.configs["recommended"] = Config.from_value(
        {
            "name": "xcube-recommended",
            "ignores": ["**/*.levels"],
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
                "xcube/time-naming": "error",
            },
        }
    )
    plugin.configs["all"] = Config.from_value(
        {
            "name": "xcube-all",
            "ignores": ["**/*.levels"],
            "plugins": {
                "xcube": plugin,
            },
            "rules": {f"xcube/{rule_id}": "error" for rule_id in plugin.rules.keys()},
        }
    )
    plugin.configs["multi-level-datasets"] = Config.from_value(
        {
            "name": "xcube-multi-level-datasets",
            "files": ["**/*.levels"],
            "ignores": ["**/*.zarr", "**/*.nc"],
            "processor": "xcube/multi-level-dataset",
        }
    )

    return plugin
