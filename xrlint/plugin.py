from dataclasses import dataclass, field
from typing import Any, Type, Callable, Literal

from xrlint.config import Config
from xrlint.processor import Processor, ProcessorOp, define_processor
from xrlint.rule import Rule, RuleOp, define_rule
from xrlint.util.formatting import format_message_type_of
from xrlint.util.importutil import import_value


@dataclass(kw_only=True)
class PluginMeta:
    """XRLint plugin metadata."""

    name: str
    """Plugin name."""

    version: str = "0.0.0"
    """Plugin version."""

    ref: str | None = None
    """Plugin module reference. 
    Specifies the location from where the plugin can be loaded.
    Must have the form "<module>:<attr>".
    """

    @classmethod
    def from_value(cls, value: Any) -> "PluginMeta":
        if isinstance(value, PluginMeta):
            return value
        if isinstance(value, dict):
            return PluginMeta(
                name=value.get("name"),
                version=value.get("version"),
                ref=value.get("ref"),
            )
        raise TypeError(format_message_type_of("value", value, "dict[str,str]"))


@dataclass(frozen=True, kw_only=True)
class Plugin:
    """An XRLint plugin."""

    meta: PluginMeta
    """Information about the plugin."""

    configs: dict[str, Config] = field(default_factory=dict)
    """A dictionary containing named configurations."""

    rules: dict[str, Rule] = field(default_factory=dict)
    """A dictionary containing the definitions of custom rules."""

    processors: dict[str, Processor] = field(default_factory=dict)
    """A dictionary containing named processors.
    """

    @classmethod
    def from_value(cls, value: Any) -> "Plugin":
        if isinstance(value, Plugin):
            return value
        if isinstance(value, dict):
            return cls._parse_plugin(value)
        if isinstance(value, str):
            plugin, plugin_ref = import_value(
                value, "export_plugin", factory=Plugin.from_value
            )
            plugin.meta.ref = plugin_ref
            return plugin
        raise TypeError(format_message_type_of("value", value, "Plugin|str"))

    def define_rule(
        self,
        name: str,
        version: str = "0.0.0",
        schema: dict[str, Any] | list[dict[str, Any]] | bool | None = None,
        type: Literal["problem", "suggestion", "layout"] | None = None,
        description: str | None = None,
        docs_url: str | None = None,
        op_class: Type[RuleOp] | None = None,
    ) -> Callable[[Any], Type[RuleOp]] | None:
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
        return define_processor(
            name=name,
            version=version,
            op_class=op_class,
            registry=self.processors,
        )

    @classmethod
    def _parse_plugin(cls, value: dict):
        return Plugin(
            meta=(Plugin._parse_meta(value)),
            rules=cls._parse_rules(value),
            processors=cls._parse_processors(value),
            configs=cls._parse_configs(value),
        )

    @classmethod
    def _parse_meta(cls, value):
        return PluginMeta.from_value(value.get("meta"))

    @classmethod
    def _parse_rules(cls, value) -> dict[str, Rule] | None:
        rules = value.get("rules", {})
        if value is None:
            return None
        if isinstance(rules, dict):
            return {k: Rule.from_value(v) for k, v in rules.items()}
        raise TypeError(format_message_type_of("rules", rules, "dict[str,Rule]|None"))

    @classmethod
    def _parse_processors(cls, value) -> dict[str, Processor] | None:
        processors = value.get("processors", {})
        if value is None:
            return None
        if isinstance(processors, dict):
            return {k: Processor.from_value(v) for k, v in processors.items()}
        raise TypeError(
            format_message_type_of("processors", processors, "dict[str,Processor]|None")
        )

    @classmethod
    def _parse_configs(cls, value) -> dict[str, Config] | None:
        configs = value.get("configs", {})
        if value is None:
            return None
        if isinstance(configs, dict):
            return {k: Config.from_value(v) for k, v in configs.items()}
        raise TypeError(
            format_message_type_of("configs", configs, "dict[str,Config]|None")
        )
