import xrlint.api as xrl


def plugin() -> xrl.Plugin:
    from .rules import import_rules

    registry = import_rules()
    return xrl.Plugin(
        meta=xrl.PluginMeta(name="core", version="0.0.1"),
        configs={
            "recommended": xrl.Config(
                name="recommended",
                rules={
                    f"{rule_id}": xrl.RuleConfig(2)
                    for rule_id, rule in registry.items()
                },
            )
        },
        rules=registry.as_dict(),
    )
