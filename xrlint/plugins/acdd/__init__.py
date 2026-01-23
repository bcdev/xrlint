from xrlint.plugin import Plugin
from xrlint.util.importutil import import_submodules


def export_plugin() -> Plugin:
    from .plugin import plugin

    import_submodules("xrlint.plugins.acdd.rules")

    rules_1_0 = {
        "acdd/1.0-attrs-highly-recommended": "error",
        "acdd/1.0-attrs-recommended": "warn",
        "acdd/1.0-attrs-suggested": "warn",
    }

    rules_1_1 = {
        "acdd/1.1-attrs-highly-recommended": "error",
        "acdd/1.1-attrs-recommended": "warn",
        "acdd/1.1-attrs-suggested": "warn",
    }

    rules_1_3 = {
        "acdd/1.3-conventions": "error",
        "acdd/1.3-attrs-highly-recommended": "error",
        "acdd/1.3-attrs-recommended": "warn",
        "acdd/1.3-attrs-suggested": "warn",
        "acdd/1.3-no-blanks-in-id": "warn",
        "acdd/1.3-metadata-link": "warn",
        "acdd/1.3-dates-iso-format": "warn",
    }

    plugin.define_config("recommended", [{"name": "recommended", "rules": rules_1_3}])

    plugin.define_config("acdd_1.3", [{"name": "ACDD 1.3", "rules": rules_1_3}])

    plugin.define_config(
        "acdd_1.3_strict_recommended",
        [
            {
                "name": "ACDD 1.3 (strict recommended)",
                "rules": {
                    **rules_1_3,
                    "1.3-attrs-recommended": "error",
                },
            },
        ],
    )

    plugin.define_config(
        "acdd_1.3_strict",
        [
            {"name": "ACDD 1.3 (strict)", "rules": dict.fromkeys(rules_1_3, "error")},
        ],
    )

    plugin.define_config(
        "acdd_1.3_warn",
        [
            {
                "name": "ACDD 1.3 (as warnings)",
                "rules": dict.fromkeys(rules_1_3, "warn"),
            },
        ],
    )

    plugin.define_config("acdd_1.1", [{"name": "ACDD 1.1", "rules": rules_1_1}])

    plugin.define_config("acdd_1.0", [{"name": "ACDD 1.0", "rules": rules_1_0}])

    return plugin
