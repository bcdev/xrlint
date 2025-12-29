from xrlint.plugin import new_plugin

plugin = new_plugin(
    "acdd",
    "1.3",
    ref="xrlint.plugins.acdd:export_plugin",
    docs_url="https://wiki.esipfed.org/Attribute_Convention_for_Data_Discovery_1-3",
)
