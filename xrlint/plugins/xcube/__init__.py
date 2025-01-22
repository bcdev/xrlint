from xrlint.plugin import Plugin
from xrlint.util.importutil import import_submodules


def export_plugin() -> Plugin:
    from .plugin import plugin

    import_submodules("xrlint.plugins.xcube.rules")
    import_submodules("xrlint.plugins.xcube.processors")

    common_configs = [
        {
            "plugins": {
                "xcube": plugin,
            },
        },
        {
            # Add *.levels to globally included list of file types
            "files": ["**/*.levels"],
        },
        {
            # Specify a processor for *.levels files
            "files": ["**/*.levels"],
            "processor": "xcube/multi-level-dataset",
        },
    ]

    plugin.define_config(
        "recommended",
        [
            *common_configs,
            {
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
            },
        ],
    )

    plugin.define_config(
        "all",
        [
            *common_configs,
            {
                "rules": {
                    f"xcube/{rule_id}": "error" for rule_id in plugin.rules.keys()
                },
            },
        ],
    )

    return plugin
