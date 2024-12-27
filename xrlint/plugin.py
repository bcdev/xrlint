from dataclasses import dataclass, field
from typing import Any

from xrlint.config import Config
from xrlint.rule import Rule
from xrlint.processor import Processor
from xrlint.util.formatting import format_message_type_of
from xrlint.util.importutil import import_value


@dataclass(frozen=True, kw_only=True)
class PluginMeta:
    """XRLint plugin metadata."""

    name: str
    """Plugin name."""

    version: str
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
    """A dictionary containing named processors."""

    @classmethod
    def from_value(cls, value: Any) -> "Plugin":
        if isinstance(value, Plugin):
            return value
        if isinstance(value, str):
            return import_value(value, "plugin", Plugin)
        raise TypeError(format_message_type_of("plugin", value, "Plugin|str"))
