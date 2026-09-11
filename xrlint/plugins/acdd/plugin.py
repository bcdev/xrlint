#  Copyright © 2026 Brockmann Consult GmbH and contributors.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from xrlint.plugin import new_plugin

plugin = new_plugin(
    "acdd",
    "1.3",
    ref="xrlint.plugins.acdd:export_plugin",
    docs_url="https://wiki.esipfed.org/Attribute_Convention_for_Data_Discovery_1-3",
)
