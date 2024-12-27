from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from xrlint.config import Config
from xrlint.rule import Rule
from xrlint.processor import Processor
from xrlint.util.importutil import import_value

if TYPE_CHECKING:
    print("----------------> TYPE_CHECKING!")
    pass


@dataclass(frozen=True, kw_only=True)
class PluginMeta:
    name: str
    version: str


@dataclass(frozen=True, kw_only=True)
class Plugin:
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
        if isinstance(value, str):
            return import_value(value, "plugin")
        return Plugin()
