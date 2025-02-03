#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).


def export_config():
    import xrlint.plugins.core
    import xrlint.plugins.xcube

    core = xrlint.plugins.core.export_plugin()
    xcube = xrlint.plugins.xcube.export_plugin()
    return [
        {
            "plugins": {
                "xcube": xcube,
            }
        },
        *core.configs["recommended"],
        *xcube.configs["recommended"],
        {
            "rules": {
                "xcube/dataset-title": "error",
                "xcube/single-grid-mapping": "off",
            }
        },
    ]
