#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

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
                "access-latency": "warn",
                "content-desc": "warn",
                "conventions": "warn",
                "coords-for-dims": "error",
                "grid-mappings": "error",
                "lat-coordinate": "error",
                "lon-coordinate": "error",
                "no-empty-attrs": "warn",
                "no-empty-chunks": "off",
                "time-coordinate": "error",
                "var-desc": "warn",
                "var-flags": "error",
                "var-missing-data": "warn",
                "var-units": "warn",
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
