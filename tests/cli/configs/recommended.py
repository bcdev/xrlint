def export_configs():
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
        core.configs["recommended"],
        xcube.configs["recommended"],
        {
            "rules": {
                "dataset-title-attr": "error",
                "xcube/single-grid-mapping": "off",
            }
        },
    ]
