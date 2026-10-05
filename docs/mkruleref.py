#  Copyright © 2025-2026 Brockmann Consult GmbH and contributors.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

import json

from xrlint.config import plugins_from_entry_points
from xrlint.constants import CORE_PLUGIN_NAME
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


def write_rule_ref_page():
    import mkdocs_gen_files

    plugins = plugins_from_entry_points()

    print(f"Generating rule reference for discovered plugins: {list(plugins.keys())}")

    with mkdocs_gen_files.open("rule-ref.md", "w") as stream:
        stream.write("# Rule Reference\n\n")
        stream.write(
            "This page is generated from plugins discovered through the "
            "`xrlint.rules` entry-point group in the build environment. "
            "Installing a plugin makes its rules available; select a preset "
            "or configure individual rules to enable them.\n\n"
            "Rule categories: :material-bug: problem, "
            ":material-lightbulb: suggestion, :material-text: layout. "
            "Preset severities: :material-lightning-bolt: error, "
            ":material-alert: warning, :material-circle-off-outline: off.\n\n"
            "Use rule identifiers in the `rules` mapping. Options follow the "
            "severity, for example `access-latency: [warn, {threshold: 5.0}]`. "
            "Schemas below describe option types, defaults, and constraints; "
            "runtime schema validation is not yet implemented. See "
            "[Configuring Rules](config.md#configuring-rules).\n\n"
            "Preset membership below summarizes rules across configuration "
            "objects; file-specific filters still determine applicability. "
            "See [Predefined Configuration Objects]"
            "(config.md#predefined-configuration-objects), including the "
            "known ACDD preset limitations.\n\n"
        )
        for plugin_name in sorted(plugins.keys()):
            plugin = plugins[plugin_name]
            display_name = (
                "core" if plugin.meta.name == CORE_PLUGIN_NAME else plugin.meta.name
            )
            stream.write(f"## {display_name} Rules\n\n")
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
        qualified_id = (
            rule_id
            if plugin.meta.name == CORE_PLUGIN_NAME
            else f"{plugin.meta.name}/{rule_id}"
        )
        stream.write(f"Rule identifier: `{qualified_id}`\n\n")
        stream.write(rule_meta.description or "_No description._")
        if rule_meta.docs_url:
            stream.write(f"\n[More...]({rule_meta.docs_url})")
        stream.write("\n\n")
        # List the predefined configurations that contain the rule
        memberships = []
        for config_id in sorted(config_rules.keys()):
            rule_configs = config_rules[config_id]
            rule_config = rule_configs.get(qualified_id)
            if rule_config is None and plugin.meta.name == CORE_PLUGIN_NAME:
                rule_config = rule_configs.get(f"{CORE_PLUGIN_NAME}/{rule_id}")
            if rule_config is not None:
                preset_id = (
                    config_id
                    if plugin.meta.name == CORE_PLUGIN_NAME
                    else f"{plugin.meta.name}/{config_id}"
                )
                memberships.append(
                    f"`{preset_id}` :{severity_icons[rule_config.severity]}:"
                )
        stream.write(
            "Contained in: " + (", ".join(memberships) or "No preset.") + "\n\n"
        )
        if rule_meta.schema is not None:
            stream.write("**Options schema**\n\n```json\n")
            stream.write(json.dumps(rule_meta.schema, indent=2, ensure_ascii=False))
            stream.write("\n```\n\n")
        else:
            stream.write("No configurable options are declared.\n\n")


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
