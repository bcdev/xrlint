from xrlint.formatter_reg import FormatterRegistry
from xrlint.util.importutil import import_submodules

registry = FormatterRegistry()


def import_formatters(dry_run: bool = False) -> FormatterRegistry:
    import_submodules("xrlint.formatters", dry_run=dry_run)
    return registry
