from dataclasses import dataclass, field
import fnmatch
from typing import Any, TYPE_CHECKING

from xrlint.util.formatting import format_message_type_of
from xrlint.util.todict import ToDictMixin
from xrlint.util.merge import (
    merge_arrays,
    merge_set_lists,
    merge_dicts,
    merge_values,
)

if TYPE_CHECKING:
    from xrlint.rule import RuleConfig
    from xrlint.plugin import Plugin


@dataclass(frozen=True, kw_only=True)
class Config(ToDictMixin):
    """Configuration object."""

    name: str | None = None
    rules: dict[str, "RuleConfig"] | None = None
    plugins: dict[str, "Plugin"] | None = None
    settings: dict[str, Any] | None = None
    linter_options: dict[str, Any] | None = None
    opener_options: dict[str, Any] | None = None

    files: list[str] | None = None
    ignores: list[str] | None = None

    @property
    def empty(self) -> bool:
        """`True` if this configuration object is empty.
        Empty means, it doesn't add configuration anything.
        """
        return not (
            self.rules or self.settings or self.linter_options or self.opener_options
        )

    def merge(self, config_obj: "Config", name: str = None) -> "Config":
        return Config(
            name=name,
            rules=self._merge_rule_dicts(self.rules, config_obj.rules),
            plugins=self._merge_plugin_dicts(self.plugins, config_obj.plugins),
            settings=self._merge_settings(self.rules, config_obj.settings),
            linter_options=self._merge_settings(
                self.linter_options, config_obj.linter_options
            ),
            opener_options=self._merge_settings(
                self.opener_options, config_obj.opener_options
            ),
            files=self._merge_pattern_lists(self.files, config_obj.files),
            ignores=self._merge_pattern_lists(self.ignores, config_obj.ignores),
        )

    @classmethod
    def from_value(cls, value: Any) -> "Config":
        if isinstance(value, Config):
            return value
        if value is None:
            return Config()
        if not isinstance(value, dict):
            raise TypeError(format_message_type_of("configuration", value, "dict"))
        if not value:
            return Config()

        rules = cls._parse_rules(value)
        plugins = cls._parse_plugins(value)
        settings = cls._parse_settings("settings", value)
        linter_options = cls._parse_settings("linter_options", value)
        opener_options = cls._parse_settings("opener_options", value)
        files = cls._parse_pattern_list(value, "files")
        ignores = cls._parse_pattern_list(value, "ignores")

        return Config(
            name=value.get("name"),
            rules=rules,
            plugins=plugins,
            settings=settings,
            linter_options=linter_options,
            opener_options=opener_options,
            files=files,
            ignores=ignores,
        )

    @classmethod
    def _merge_rule_dicts(
        cls,
        rules1: dict[str, "RuleConfig"] | None,
        rules2: dict[str, "RuleConfig"] | None,
    ) -> dict[str, "RuleConfig"] | None:
        from xrlint.rule import RuleConfig

        def merge_items(r1: RuleConfig, r2: RuleConfig) -> RuleConfig:
            if r1.severity == r2.severity:
                return RuleConfig(
                    r2.severity,
                    merge_arrays(r1.args, r2.args),
                    merge_dicts(r1.kwargs, r2.kwargs),
                )
            return r2

        return merge_dicts(rules1, rules2, merge_items=merge_items)

    @classmethod
    def _merge_plugin_dicts(
        cls,
        plugins1: dict[str, "Plugin"] | None,
        plugins2: dict[str, "Plugin"] | None,
    ) -> dict[str, "RuleConfig"] | None:
        from xrlint.plugin import Plugin

        def merge_items(_p1: Plugin, p2: Plugin) -> Plugin:
            return p2

        return merge_dicts(plugins1, plugins2, merge_items=merge_items)

    @classmethod
    def _merge_settings(
        cls, settings1: dict[str, Any] | None, settings2: dict[str, Any] | None
    ) -> dict[str, Any] | None:
        return merge_dicts(settings1, settings2, merge_items=merge_values)

    @classmethod
    def _merge_pattern_lists(
        cls, patterns1: list[str] | None, patterns2: list[str] | None
    ) -> list[str] | None:
        return merge_set_lists(patterns1, patterns2)

    @classmethod
    def _parse_rules(cls, config_dict: dict) -> dict[str, "RuleConfig"]:
        from xrlint.rule import RuleConfig

        rules = config_dict.get("rules")
        if isinstance(rules, dict):
            return {rn: RuleConfig.from_value(rc) for rn, rc in rules.items()}
        if rules is not None:
            raise TypeError(
                format_message_type_of("rules configuration", rules, "dict")
            )

    @classmethod
    def _parse_plugins(cls, config_dict: dict) -> dict[str, "Plugin"]:
        from xrlint.plugin import Plugin

        plugins = config_dict.get("plugins")
        if isinstance(plugins, dict):
            return {k: Plugin.from_value(v) for k, v in plugins.items()}
        if plugins is not None:
            raise TypeError(
                format_message_type_of("plugins configuration", plugins, "dict")
            )

    @classmethod
    def _parse_settings(cls, name: str, config_dict: dict) -> dict[str, Any]:
        settings = config_dict.get("settings")
        if isinstance(settings, dict):
            for k, v in settings.items():
                if not isinstance(k, str):
                    raise TypeError(format_message_type_of(f"{name} keys", k, str))
            return {k: v for k, v in settings.items()}
        if settings is not None:
            raise TypeError(format_message_type_of(name, settings, "dict[str,Any]"))

    @classmethod
    def _parse_pattern_list(cls, config_dict: dict, name) -> list[str]:
        patterns = config_dict.get(name)
        if isinstance(patterns, list):
            return [cls._parse_pattern(name, v) for v in patterns]
        if patterns is not None:
            raise TypeError(
                format_message_type_of(f"{name} configuration", patterns, "list[str]")
            )

    @classmethod
    def _parse_pattern(cls, name, pattern):
        if not isinstance(pattern, str):
            raise TypeError(
                format_message_type_of(f"pattern in {name} configuration", pattern, str)
            )


def merge_configs(
    config1: Config | dict[str, Any] | None,
    config2: Config | dict[str, Any] | None,
) -> Config:
    if config1 is not None:
        config1 = Config.from_value(config1)
    else:
        config1 = Config()
    if config2 is not None:
        config2 = Config.from_value(config2)
    else:
        config2 = Config()
    return config1.merge(config2)


@dataclass(frozen=True)
class ConfigList:
    configs: list[Config] = field(default_factory=list)

    def resolve_for_path(self, path: str) -> Config | None:
        # Step 1: Check against global ignores
        global_ignores = set()
        for c in self.configs:
            if c.ignores and c.empty:  # global ignores
                global_ignores.update(c.ignores)
        for p in global_ignores:
            if fnmatch.fnmatch(path, p):
                return None

        # Step 2: Check against global ignores
        config = Config()
        for c in self.configs:
            matches = True
            if c.ignores:
                for p in c.ignores:
                    matches = fnmatch.fnmatch(path, p)
                    if not matches:
                        break
            if matches:
                if c.files:
                    for p in c.files:
                        matches = fnmatch.fnmatch(path, p)
                        if matches:
                            break
            if matches:
                config = config.merge(c)

        return config

    @classmethod
    def from_value(cls, value: Any) -> "ConfigList":
        if isinstance(value, ConfigList):
            return value
        if isinstance(value, list):
            return ConfigList([Config.from_value(c) for c in value])
        raise TypeError(
            format_message_type_of(
                "configuration list", value, "ConfigList|list[Config|dict]"
            )
        )
