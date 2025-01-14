from xrlint.plugin import Plugin

severity_icons = {
    2: "material-lightning-bolt",
    1: "material-alert",
    0: "material-circle-off-outline",
}

rule_type_icons = {
    "problem": "material-bug",
    "suggestion": "material-lightbulb",
    "layout": "material-text",
}


def write_rule_ref_page():
    import xrlint.plugins.core
    import xrlint.plugins.xcube

    core = xrlint.plugins.core.export_plugin()
    xcube = xrlint.plugins.xcube.export_plugin()
    with open("docs/rule-ref.md", "w") as stream:
        stream.write("# Rule Reference\n\n")
        stream.write(
            "This page is auto-generated from XRLint's builtin"
            " rules (`python -m mkruleref`).\n"
            "New rules will be added by upcoming XRLint releases.\n\n"
        )
        stream.write("## Core Rules\n\n")
        write_plugin_rules(stream, core)
        stream.write("## xcube Rules\n\n")
        write_plugin_rules(stream, xcube)


def write_plugin_rules(stream, plugin: Plugin):
    configs = plugin.configs
    for rule_id in sorted(plugin.rules.keys()):
        rule_meta = plugin.rules[rule_id].meta
        stream.write(
            f"### :{rule_type_icons.get(rule_meta.type)}: `{rule_meta.name}`\n\n"
        )
        stream.write(rule_meta.description or "_No description._")
        if rule_meta.docs_url:
            stream.write(f"\n[More information.]({rule_meta.docs_url})")
        stream.write("\n\n")
        # List the predefined configurations that contain the rule
        stream.write("Contained in: ")
        for config_id in sorted(configs.keys()):
            config = configs[config_id]
            rule_configs = config.rules or {}
            rule_config = rule_configs.get(rule_id) or rule_configs.get(
                f"{plugin.meta.name}/{rule_id}"
            )
            if rule_config is not None:
                stream.write(f" `{config_id}`-:{severity_icons[rule_config.severity]}:")
        stream.write("\n\n")


if __name__ == "__main__":
    write_rule_ref_page()
