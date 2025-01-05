from dataclasses import dataclass, field
from typing import Any, Type, Callable, Literal

from xrlint.config import Config
from xrlint.processor import Processor, ProcessorOp, register_processor
from xrlint.rule import Rule, RuleOp, register_rule
from xrlint.util.formatting import format_message_type_of
from xrlint.util.importutil import import_value


@dataclass(frozen=True, kw_only=True)
class PluginMeta:
    """XRLint plugin metadata."""

    name: str
    """Plugin name."""

    version: str = "0.0.0"
    """Plugin version."""


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
        if isinstance(value, str):
            return import_value(value, "export_plugin", Plugin.from_value)
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
        return register_rule(
            self.rules,
            name=name,
            version=version,
            schema=schema,
            type=type,
            description=description,
            docs_url=docs_url,
            op_class=op_class,
        )

    def define_processor(
        self,
        name: str,
        version: str = "0.0.0",
        op_class: Type[ProcessorOp] | None = None,
    ):
        return register_processor(
            self.processors,
            name=name,
            version=version,
            op_class=op_class,
        )
