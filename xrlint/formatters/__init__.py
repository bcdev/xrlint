#  Copyright © 2025-2026 Brockmann Consult GmbH and contributors.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from xrlint.formatter import FormatterRegistry
from xrlint.util.importutil import import_submodules

registry = FormatterRegistry()


def export_formatters() -> FormatterRegistry:
    import_submodules("xrlint.formatters")
    return registry
