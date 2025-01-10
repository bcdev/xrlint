from xrlint.plugin import Plugin
from xrlint.plugin import PluginMeta
from xrlint.version import version


plugin = Plugin(
    meta=PluginMeta(
        name="xcube",
        version=version,
        ref="xrlint.plugins.xcube:export_plugin",
    )
)
