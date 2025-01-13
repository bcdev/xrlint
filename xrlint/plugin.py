from dataclasses import dataclass, field
from typing import Any, Type, Callable, Literal

from xrlint.config import Config
from xrlint.processor import Processor, ProcessorOp, define_processor
from xrlint.rule import Rule, RuleOp, define_rule
from xrlint.util.codec import MappingConstructible, T
from xrlint.util.formatting import format_message_type_of
from xrlint.util.importutil import import_value


@dataclass(kw_only=True)
class PluginMeta(MappingConstructible):
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
    def _get_value_type_name(cls) -> str:
        return "PluginMeta | dict"


@dataclass(frozen=True, kw_only=True)
class Plugin(MappingConstructible):
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
    def _from_str(cls, value: str, value_name: str) -> T:
        plugin, plugin_ref = import_value(
            value, "export_plugin", factory=Plugin.from_value
        )
        plugin.meta.ref = plugin_ref
        return plugin

    @classmethod
    def _get_value_type_name(cls) -> str:
        return "Plugin | dict | str"
