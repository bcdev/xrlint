from xrlint.formatter import FormatterRegistry
from xrlint.util.importutil import import_submodules

registry = FormatterRegistry()


def export_formatters() -> FormatterRegistry:
    import_submodules("xrlint.formatters")
    return registry
