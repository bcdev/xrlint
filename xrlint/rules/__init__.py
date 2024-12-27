from xrlint.rule_reg import RuleRegistry
from xrlint.util.importutil import import_submodules

registry = RuleRegistry()


def import_rules(dry_run: bool = False) -> RuleRegistry:
    import_submodules("xrlint.rules", dry_run=dry_run)
    return registry
