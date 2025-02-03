#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from dataclasses import dataclass, field
from typing import Any, Callable, Literal, Type

from xrlint.config import Config, ConfigLike, ConfigObject
from xrlint.processor import Processor, ProcessorOp, define_processor
from xrlint.rule import Rule, RuleOp, define_rule
from xrlint.util.constructible import MappingConstructible
from xrlint.util.importutil import import_value
from xrlint.util.serializable import JsonSerializable, JsonValue


@dataclass(kw_only=True)
class PluginMeta(MappingConstructible, JsonSerializable):
    """Plugin metadata."""

    name: str
    """Plugin name."""

    version: str = "0.0.0"
    """Plugin version."""

    ref: str | None = None
    """Plugin reference.
    Specifies the location from where the plugin can be
    dynamically imported.
    Must have the form "<module>:<attr>", if given.
    """

    docs_url: str | None = None
    """Plugin documentation URL."""

    @classmethod
    def value_name(cls) -> str:
        return "plugin_meta"

    @classmethod
    def value_type_name(cls) -> str:
        return "PluginMeta | dict"


@dataclass(frozen=True, kw_only=True)
class Plugin(MappingConstructible, JsonSerializable):
    """A plugin that can contribute rules, processors,
    and predefined configurations to XRLint.

    Use the factory [new_plugin][xrlint.plugin.new_plugin]
    to create plugin instances.
    """

    meta: PluginMeta
    """Information about the plugin."""

    rules: dict[str, Rule] = field(default_factory=dict)
    """A dictionary containing the definitions of custom rules."""

    processors: dict[str, Processor] = field(default_factory=dict)
    """A dictionary containing named processors.
    """

    configs: dict[str, list[ConfigObject]] = field(default_factory=dict)
    """A dictionary containing named configuration lists."""

    def define_rule(
        self,
        name: str,
        version: str = "0.0.0",
        schema: dict[str, Any] | list[dict[str, Any]] | bool | None = None,
        type: Literal["problem", "suggestion", "layout"] = "problem",
        description: str | None = None,
        docs_url: str | None = None,
        op_class: Type[RuleOp] | None = None,
    ) -> Callable[[Any], Type[RuleOp]] | None:
        """Decorator to define a plugin rule.
        The method registers a new rule with the plugin.

        Refer to [define_rule][xrlint.rule.define_rule]
        for details.
        """
        return define_rule(
            name=name,
            version=version,
            schema=schema,
            type=type,
            description=description,
            docs_url=docs_url,
            op_class=op_class,
            registry=self.rules,
        )

    def define_processor(
        self,
        name: str | None = None,
        version: str = "0.0.0",
        op_class: Type[ProcessorOp] | None = None,
    ):
        """Decorator to define a plugin processor.
        The method registers a new processor with the plugin.

        Refer to [define_processor][xrlint.processor.define_processor]
        for details.
        """
        return define_processor(
            name=name,
            version=version,
            op_class=op_class,
            registry=self.processors,
        )

    def define_config(self, name: str, config: ConfigLike) -> Config:
        """Define a named configuration.

        Args:
            name: The name of the configuration.
            config: A configuration-like value.
                For more information see the
                [ConfigLike][xrlint.config.ConfigLike] type alias.

        Returns:
            The configuration.
        """
        config = Config.from_value(config)
        self.configs[name] = list(config.objects)
        return config

    @classmethod
    def _from_str(cls, value: str, value_name: str) -> "Plugin":
        plugin, plugin_ref = import_value(
            value, "export_plugin", factory=Plugin.from_value
        )
        plugin.meta.ref = plugin_ref
        return plugin

    @classmethod
    def value_name(cls) -> str:
        return "plugin"

    @classmethod
    def value_type_name(cls) -> str:
        return "Plugin | dict | str"

    def to_json(self, value_name: str | None = None) -> JsonValue:
        if self.meta.ref:
            return self.meta.ref
        return super().to_json(value_name=value_name)


def new_plugin(
    name: str,
    version: str = "0.0.0",
    ref: str | None = None,
    docs_url: str | None = None,
    rules: dict[str, Rule] | None = None,
    processors: dict[str, Processor] | None = None,
    configs: dict[str, ConfigObject] | None = None,
) -> Plugin:
    """Create a new plugin object that can contribute rules, processors,
    and predefined configurations to XRLint.

    Args:
        name: Plugin name. Required.
        version: Plugin version. Defaults to `"0.0.0"`.
        ref: Plugin reference. Optional.
        docs_url: Plugin documentation URL. Optional.
        rules: A dictionary containing the definitions of custom rules. Optional.
        processors: A dictionary containing custom processors. Optional.
        configs: A dictionary containing predefined configurations. Optional.
    """
    return Plugin(
        meta=PluginMeta(name=name, version=version, ref=ref, docs_url=docs_url),
        rules=rules or {},
        processors=processors or {},
        configs=configs or {},
    )
