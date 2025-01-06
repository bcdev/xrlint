from dataclasses import dataclass, field
from functools import cached_property
from typing import Any, TYPE_CHECKING, Union

from xrlint.constants import CORE_PLUGIN_NAME
from xrlint.util.filefilter import FileFilter
from xrlint.util.formatting import format_message_type_of
from xrlint.util.todict import ToDictMixin
from xrlint.util.merge import (
    merge_arrays,
    merge_set_lists,
    merge_dicts,
    merge_values,
)


if TYPE_CHECKING:  # pragma: no cover
    from xrlint.rule import Rule
    from xrlint.rule import RuleConfig
    from xrlint.plugin import Plugin
    from xrlint.processor import ProcessorOp


def get_core_plugin() -> "Plugin":
    """Get the fully imported, populated core plugin."""
    from xrlint.plugins.core import export_plugin

    return export_plugin()


def get_core_config(recommended: bool = False):
    """Create a base configuration for the built-in plugins.

    Args:
        recommended: `True` (the default) if the recommended
            rule configurations of the built-in plugins should be used.
    Returns:
        A new `Config` object
    """
    core_plugin = get_core_plugin()
    return Config(
        plugins={
            CORE_PLUGIN_NAME: core_plugin,
        },
        rules=core_plugin.configs["recommended"].rules if recommended else None,
    )


def split_config_spec(config_spec: str) -> tuple[str, str]:
    """Split a configuration specification into plugin name
    and configuration item name.
    """
    return (
        config_spec.split("/", maxsplit=1)
        if "/" in config_spec
        else (CORE_PLUGIN_NAME, config_spec)
    )


def merge_configs(
    config1: Union["Config", dict[str, Any], None],
    config2: Union["Config", dict[str, Any], None],
) -> "Config":
    """Merge two configuration objects and return the result."""
    config1 = Config.from_value(config1)
    config2 = Config.from_value(config2)
    return config1.merge(config2)


@dataclass(frozen=True, kw_only=True)
class Config(ToDictMixin):
    """Configuration object.
    A configuration object contains all the information XRLint
    needs to execute on a set of dataset files.

    You should not use the class constructor directly.
    Instead, use the `Config.from_value()` function.
    """

    name: str | None = None
    """A name for the configuration object.
    This is used in error messages and config inspector to help identify
    which configuration object is being used.
    """

    files: list[str] | None = None
    """An array of glob patterns indicating the files that the
    configuration object should apply to. If not specified,
    the configuration object applies to all files matched
    by any other configuration object.

    When a configuration object contains only the files property
    without accompanying rules or settings, it effectively acts as
    a _global file filter_. This means that XRLint will recognize
    and process only the files matching these patterns, thereby
    limiting its scope to the specified files. The inbuilt
    global file filters are `["**/*.zarr", "**/*.nc"]`.
    """

    ignores: list[str] | None = None
    """An array of glob patterns indicating the files that the
    configuration object should not apply to. If not specified,
    the configuration object applies to all files matched by `files`.
    If `ignores` is used without any other keys in the configuration
    object, then the patterns act as _global ignores_.
    """

    linter_options: dict[str, Any] | None = None
    """A dictionary containing options related to the linting process."""

    opener_options: dict[str, Any] | None = None
    """A dictionary containing options that are passed to
    the dataset opener.
    """

    processor: Union["ProcessorOp", str, None] = None
    """Either an object compatible with the `ProcessorOp`
    interface or a string indicating the name of a processor inside
    of a plugin (i.e., `"pluginName/processorName"`).
    """

    plugins: dict[str, "Plugin"] | None = None
    """A dictionary containing a name-value mapping of plugin names to
    plugin objects. When `files` is specified, these plugins are only
    available to the matching files.
    """

    rules: dict[str, "RuleConfig"] | None = None
    """A dictionary containing the configured rules.
    When `files` or `ignores` are specified, these rule configurations
    are only available to the matching files.
    """

    settings: dict[str, Any] | None = None
    """A dictionary containing name-value pairs of information
    that should be available to all rules.
    """

    @classmethod
    def from_value(cls, value: Any) -> "Config":
        """Convert given `value` into a `Config` object.

        If `value` is already a `Config` then it is returned as-is.

        Args:
            value: A `Config` object, a `dict` containing the
                configuration properties, or `None` which
                converts into an empty configuration.
        Returns:
            A `Config` object.
        """
        if isinstance(value, Config):
            return value
        if value is None:
            return Config()
        if not isinstance(value, dict):
            raise TypeError(format_message_type_of("configuration", value, "dict"))
        if not value:
            return Config()

        files = cls._parse_pattern_list(value, "files")
        ignores = cls._parse_pattern_list(value, "ignores")
        linter_options = cls._parse_options("linter_options", value)
        opener_options = cls._parse_options("opener_options", value)
        processor = cls._parse_processor(value)
        plugins = cls._parse_plugins(value)
        rules = cls._parse_rules(value)
        settings = cls._parse_options("settings", value)

        return Config(
            name=value.get("name"),
            files=files,
            ignores=ignores,
            linter_options=linter_options,
            opener_options=opener_options,
            processor=processor,
            plugins=plugins,
            rules=rules,
            settings=settings,
        )

    @cached_property
    def file_filter(self) -> "FileFilter":
        """The file filter specified by this configuration. May be empty."""
        return FileFilter.from_patterns(self.files, self.ignores)

    @cached_property
    def empty(self) -> bool:
        """`True` if this configuration object does not configure anything.
        Note, it could still contribute to a global file filter if its
        `files` and `ignores` options are set."""
        return not (
            self.linter_options
            or self.opener_options
            or self.plugins
            or self.rules
            or self.settings
        )

    def get_plugin(self, plugin_name: str) -> "Plugin":
        """Get the plugin for given plugin name `plugin_name`."""
        plugin = (self.plugins or {}).get(plugin_name)
        if plugin is None:
            raise ValueError(f"unknown plugin {plugin_name!r}")
        return plugin

    def get_rule(self, rule_id: str) -> "Rule":
        """Get the rule for the given rule identifier `rule_id`.

        Args:
            rule_id: The rule identifier including plugin namespace, if any.
                Format `<rule-name>` (builtin rules) or `<plugin-name>/<rule-name>`.
        Returns:
            A `Rule` object.
        Raises:
            ValueError: If either the plugin is unknown in this configuration
                or the rule name is unknown.
        """
        plugin_name, rule_name = split_config_spec(rule_id)
        plugin = self.get_plugin(plugin_name)
        rule = (plugin.rules or {}).get(rule_name)
        if rule is None:
            raise ValueError(f"unknown rule {rule_id!r}")
        return rule

    def get_processor_op(
        self, processor_spec: Union["ProcessorOp", str]
    ) -> "ProcessorOp":
        """Get the processor operation for the given
        processor identifier `processor_spec`.
        """
        from xrlint.processor import Processor
        from xrlint.processor import ProcessorOp

        if isinstance(processor_spec, ProcessorOp):
            return processor_spec

        plugin_name, processor_name = split_config_spec(processor_spec)
        plugin = self.get_plugin(plugin_name)
        processor: Processor | None = (plugin.processors or {}).get(processor_name)
        if processor is None:
            raise ValueError(f"unknown processor {processor_spec!r}")
        return processor.op_class()

    def merge(self, config: "Config", name: str = None) -> "Config":
        return Config(
            name=name,
            files=self._merge_pattern_lists(self.files, config.files),
            ignores=self._merge_pattern_lists(self.ignores, config.ignores),
            linter_options=self._merge_options(
                self.linter_options, config.linter_options
            ),
            opener_options=self._merge_options(
                self.opener_options, config.opener_options
            ),
            processor=merge_values(self.processor, config.processor),
            plugins=self._merge_plugin_dicts(self.plugins, config.plugins),
            rules=self._merge_rule_dicts(self.rules, config.rules),
            settings=self._merge_options(self.settings, config.settings),
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
    def _merge_pattern_lists(
        cls, patterns1: list[str] | None, patterns2: list[str] | None
    ) -> list[str] | None:
        return merge_set_lists(patterns1, patterns2)

    @classmethod
    def _merge_options(
        cls, settings1: dict[str, Any] | None, settings2: dict[str, Any] | None
    ) -> dict[str, Any] | None:
        return merge_dicts(settings1, settings2, merge_items=merge_values)

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
        return pattern

    @classmethod
    def _parse_processor(cls, config_dict: dict) -> Union["ProcessorOp", str, None]:
        from xrlint.processor import ProcessorOp

        processor = config_dict.get("processor")
        if processor is None or isinstance(processor, (str, ProcessorOp)):
            return processor
        raise TypeError(
            format_message_type_of(
                "processor configuration", processor, "ProcessorOp|str|None"
            )
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
    def _parse_options(cls, name: str, config_dict: dict) -> dict[str, Any]:
        settings = config_dict.get(name)
        if isinstance(settings, dict):
            for k, v in settings.items():
                if not isinstance(k, str):
                    raise TypeError(format_message_type_of(f"{name} keys", k, str))
            return {k: v for k, v in settings.items()}
        if settings is not None:
            raise TypeError(format_message_type_of(name, settings, "dict[str,Any]"))


@dataclass(frozen=True)
class ConfigList:
    """A holder for a list of `Config` objects.

    You should not use the class constructor directly.
    Instead, use the `ConfigList.from_value()` function.
    """

    configs: list[Config] = field(default_factory=list)
    """The list of `Config` objects."""

    @classmethod
    def from_value(cls, value: Any) -> "ConfigList":
        """Convert given `value` into a `ConfigList` object.

        If `value` is already a `ConfigList` then it is returned as-is.

        Args:
            value: A `ConfigList` object or `list` of items which can be
                converted into `Config` objects including configuration
                names of tyype `str`. The latter are resolved against
                the plugin configurations seen so far in the list.
        Returns:
            A `ConfigList` object.
        """
        if isinstance(value, ConfigList):
            return value

        if not isinstance(value, list):
            raise TypeError(
                format_message_type_of(
                    "configuration list", value, "ConfigList|list[Config|dict|str]"
                )
            )

        configs: list[Config] = []
        plugins: dict[str, Plugin] = {}
        for item in value:
            if isinstance(item, str):
                if CORE_PLUGIN_NAME not in plugins:
                    plugins.update({CORE_PLUGIN_NAME: get_core_plugin()})
                config = cls._get_named_config(item, plugins)
            else:
                config = Config.from_value(item)
            configs.append(config)
            plugins.update(config.plugins if config.plugins else {})

        return ConfigList(configs)

    @classmethod
    def _get_named_config(cls, config_spec: str, plugins: dict[str, "Plugin"]):
        plugin_name, config_name = (
            config_spec.split("/", maxsplit=1)
            if "/" in config_spec
            else (CORE_PLUGIN_NAME, config_spec)
        )
        plugin: Plugin | None = plugins.get(plugin_name)
        if plugin is None or not plugin.configs or config_name not in plugin.configs:
            raise ValueError(f"configuration {config_spec!r} not found")
        config_value = plugin.configs[config_name]
        return config_value

    def get_global_filter(self, default: FileFilter | None = None) -> "FileFilter":
        """Get a global file filter for this configuration list."""
        global_filter = FileFilter(
            default.files if default else (),
            default.ignores if default else (),
        )
        for c in self.configs:
            if c.empty and not c.file_filter.empty:
                global_filter = global_filter.merge(c.file_filter)
        return global_filter

    def compute_config(self, file_path: str) -> Config | None:
        """Compute the configuration object for the given file path.

        Args:
            file_path: A dataset file path.
        Returns:
            A `Config` object which may be empty, or `None`
            if `file_path` is not included by any `files` pattern
            or intentionally ignored by global `ignores`.
        """

        config = None
        for c in self.configs:
            if c.file_filter.empty or c.file_filter.accept(file_path):
                config = config.merge(c) if config is not None else c

        if config is None:
            return None

        # Note, computed configurations do not have "files" and "ignores"
        return Config(
            name="<computed>",
            linter_options=config.linter_options,
            opener_options=config.opener_options,
            processor=config.processor,
            plugins=config.plugins,
            rules=config.rules,
            settings=config.settings,
        )
