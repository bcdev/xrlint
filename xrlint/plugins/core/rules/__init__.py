from xrlint.constants import CORE_PLUGIN_NAME
from xrlint.plugin import Plugin
from xrlint.plugin import PluginMeta
from xrlint.version import version


plugin = Plugin(
    meta=PluginMeta(
        name=CORE_PLUGIN_NAME,
        version=version,
        ref="xrlint.plugins.core:export_plugin",
    )
)
