from xrlint.constants import CORE_PLUGIN_NAME, CORE_DOCS_URL
from xrlint.plugin import new_plugin
from xrlint.version import version

plugin = new_plugin(
    name=CORE_PLUGIN_NAME,
    version=version,
    ref="xrlint.plugins.core:export_plugin",
    docs_url=CORE_DOCS_URL,
)
