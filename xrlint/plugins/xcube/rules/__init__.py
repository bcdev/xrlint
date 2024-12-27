from xrlint.rule_reg import RuleRegistry
from xrlint.util.importutil import import_submodules

registry = RuleRegistry()


def import_rules() -> RuleRegistry:
    import_submodules("xrlint.plugins.xcube.rules")
    return registry
