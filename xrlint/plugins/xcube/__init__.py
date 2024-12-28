import xrlint.api as xrl
from .rules import registry


def plugin() -> xrl.Plugin:
    from .rules import import_rules

    registry = import_rules()

    return xrl.Plugin(
        meta=xrl.PluginMeta(name="xcube", version="0.0.1"),
        configs={
            "recommended": xrl.Config(
                name="xcube-recommended",
                rules={
                    f"xcube/{rule_id}": xrl.RuleConfig(2)
                    for rule_id, rule in registry.items()
                },
            )
        },
        rules=registry.as_dict(),
    )
