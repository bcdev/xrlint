#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from xrlint.constants import CORE_DOCS_URL, CORE_PLUGIN_NAME
from xrlint.plugin import new_plugin
from xrlint.version import version

plugin = new_plugin(
    name=CORE_PLUGIN_NAME,
    version=version,
    ref="xrlint.plugins.core:export_plugin",
    docs_url=CORE_DOCS_URL,
)
