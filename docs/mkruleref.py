#  Copyright © 2025-2026 Brockmann Consult GmbH and contributors.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from xrlint.config import plugins_from_entry_points
from xrlint.plugin import Plugin
from xrlint.rule import RuleConfig

# for icons, see
# https://squidfunk.github.io/mkdocs-material/reference/icons-emojis/

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

# read_more_icon = "material-book-open-outline"
read_more_icon = "material-information-variant"


def write_rule_ref_page():
    import mkdocs_gen_files

    plugins = plugins_from_entry_points()

    print(f"Generating rule reference for discovered plugins: {list(plugins.keys())}")

    with mkdocs_gen_files.open("rule-ref.md", "w") as stream:
        stream.write("# Rule Reference\n\n")
        stream.write(
            "This page is auto-generated from XRLint's builtin"
            " rules.\n"
            "New rules will be added by upcoming XRLint releases.\n\n"
        )
        for plugin_name in sorted(plugins.keys()):
            plugin = plugins[plugin_name]
            stream.write(f"## {plugin.meta.name} Rules\n\n")
            if plugin.meta.ref:
                stream.write(f"- `{plugin.meta.ref.removesuffix(':export_plugin')}`\n")
            if plugin.meta.docs_url:
                stream.write(f"- [Documentation]({plugin.meta.docs_url})\n\n")
            write_plugin_rules(stream, plugin)


def write_plugin_rules(stream, plugin: Plugin):
    config_rules = get_plugin_rule_configs(plugin)
    for rule_id in sorted(plugin.rules.keys()):
        rule_meta = plugin.rules[rule_id].meta
        stream.write(
            f"### :{rule_type_icons.get(rule_meta.type)}: `{rule_meta.name}`\n\n"
        )
        stream.write(rule_meta.description or "_No description._")
        if rule_meta.docs_url:
            stream.write(f"\n[More...]({rule_meta.docs_url})")
        stream.write("\n\n")
        # List the predefined configurations that contain the rule
        stream.write("Contained in: ")
        for config_id in sorted(config_rules.keys()):
            rule_configs = config_rules[config_id]
            rule_config = rule_configs.get(rule_id) or rule_configs.get(
                f"{plugin.meta.name}/{rule_id}"
            )
            if rule_config is not None:
                stream.write(f" `{config_id}`-:{severity_icons[rule_config.severity]}:")
        stream.write("\n\n")


def get_plugin_rule_configs(plugin: Plugin) -> dict[str, dict[str, RuleConfig]]:
    configs = plugin.configs
    config_rules: dict[str, dict[str, RuleConfig]] = {}
    for config_name, config_list in configs.items():
        # note, here we assume most plugins configure their rules
        # in one dedicated config object only. However, this is not
        # the general case as file patterns may be used to make the
        # rules configurations specific.
        rule_configs = {}
        for config in config_list:
            if config.rules:
                rule_configs.update(config.rules)
        config_rules[config_name] = rule_configs
    return config_rules


write_rule_ref_page()
