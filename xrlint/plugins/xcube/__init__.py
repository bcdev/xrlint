#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from xrlint.plugin import Plugin
from xrlint.plugins.xcube.constants import ML_FILE_PATTERN
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
            "files": [ML_FILE_PATTERN],
        },
        {
            # Specify a processor for *.levels files
            "files": [ML_FILE_PATTERN],
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
                    "xcube/dataset-title": "error",
                    "xcube/grid-mapping-naming": "warn",
                    "xcube/increasing-time": "error",
                    "xcube/lat-lon-naming": "error",
                    "xcube/ml-dataset-meta": "error",
                    "xcube/ml-dataset-time": "warn",
                    "xcube/ml-dataset-xy": "error",
                    "xcube/no-chunked-coords": "warn",
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
