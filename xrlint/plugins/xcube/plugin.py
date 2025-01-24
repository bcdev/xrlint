from xrlint.plugin import new_plugin
from xrlint.version import version

plugin = new_plugin(
    name="xcube",
    version=version,
    ref="xrlint.plugins.xcube:export_plugin",
)
