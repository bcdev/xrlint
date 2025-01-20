from xrlint.constants import CORE_PLUGIN_NAME
from xrlint.plugin import new_plugin
from xrlint.version import version

plugin = new_plugin(
    name=CORE_PLUGIN_NAME,
    version=version,
    ref="xrlint.plugins.core:export_plugin",
)
