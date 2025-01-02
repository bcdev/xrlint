from xrlint.plugin import Plugin


def write_rule_ref_page():
    import xrlint.plugins.core
    import xrlint.plugins.xcube

    core = xrlint.plugins.core.export_plugin()
    xcube = xrlint.plugins.xcube.export_plugin()
    with open("docs/rule-ref.md", "w") as stream:
        stream.write("# Rule Reference\n\n")
        stream.write("## Core Rules\n\n")
        write_plugin_rules(stream, core)
        stream.write("## xcube Rules\n\n")
        write_plugin_rules(stream, xcube)


def write_plugin_rules(stream, plugin: Plugin):
    for rule_id in sorted(plugin.rules.keys()):
        rule_meta = plugin.rules[rule_id].meta
        stream.write(f"### `{rule_meta.name}`\n\n")
        stream.write(rule_meta.description or "_No description._")
        stream.write(f"\n\n")


if __name__ == "__main__":
    write_rule_ref_page()
