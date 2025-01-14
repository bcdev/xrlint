from dataclasses import dataclass, field
from functools import cached_property
from typing import Any, TYPE_CHECKING, Union, Literal, Sequence

from xrlint.constants import CORE_PLUGIN_NAME
from xrlint.util.codec import (
    MappingConstructible,
    ValueConstructible,
    JsonSerializable,
    JsonValue,
)
from xrlint.util.filefilter import FileFilter
from xrlint.util.merge import (
    merge_arrays,
    merge_set_lists,
    merge_dicts,
    merge_values,
)


if TYPE_CHECKING:  # pragma: no cover
    # make IDEs and flake8 happy
    from xrlint.rule import Rule
    from xrlint.rule import RuleConfig
    from xrlint.plugin import Plugin
    from xrlint.processor import ProcessorOp


def get_core_plugin() -> "Plugin":
    """Get the fully imported, populated core plugin."""
    from xrlint.plugins.core import export_plugin

    return export_plugin()


def get_core_config(
    config_name: Literal["all", "recommended"] | None = None
) -> "Config":
    """Create a base configuration for the built-in plugins.

    Args:
        config_name: `"recommended"` if the recommended configuration
            of the builtin rules should be used, or `"all"` if all rules
            shall be used. Pass `None` (the default) if you don't want this.
            In the latter case, you should configure the `rules`
            option either in `config` or `config_kwargs`. Otherwise, calling
            `verify_dataset()` without any rule configuration will never
            succeed for any given dataset.

    Returns:
        A new `Config` object
    """
    core_plugin = get_core_plugin()
    config = Config(
        plugins={
            CORE_PLUGIN_NAME: core_plugin,
        },
    )
    if config_name:
        return config.merge(core_plugin.configs[config_name])
    else:
        return config


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
class Config(MappingConstructible, JsonSerializable):
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

    @cached_property
    def file_filter(self) -> FileFilter:
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
            rule_id: The rule identifier including plugin namespace,
                if any. Format `<rule-name>` (builtin rules) or
                `<plugin-name>/<rule-name>`.

        Returns:
            A `Rule` object.

        Raises:
            ValueError: If either the plugin is unknown in this
                configuration or the rule name is unknown.
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
    def _from_none(cls, value_name: str) -> "Config":
        return Config()

    @classmethod
    def _get_forward_refs(cls) -> dict[str, type]:
        from xrlint.processor import ProcessorOp
        from xrlint.plugin import Plugin
        from xrlint.rule import Rule
        from xrlint.rule import RuleConfig

        return {
            "ProcessorOp": ProcessorOp,
            "Plugin": Plugin,
            "Rule": Rule,
            "RuleConfig": RuleConfig,
        }

    @classmethod
    def _get_value_name(cls) -> str:
        return "config"

    @classmethod
    def _get_value_type_name(cls) -> str:
        return "Config | dict | None"

    def to_dict(self, value_name: str | None = None) -> dict[str, JsonValue]:
        return {k: v for k, v in super().to_dict().items() if v is not None}


@dataclass(frozen=True)
class ConfigList(ValueConstructible, JsonSerializable):
    """A holder for a list of configuration objects of
    type [Config][xrlint.config.Config].

    You should not use the class constructor directly.
    Instead, use the `ConfigList.from_value()` function.
    """

    configs: list[Config] = field(default_factory=list)
    """The list of configuration objects."""

    def get_global_filter(self, default: FileFilter | None = None) -> FileFilter:
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

    @classmethod
    def from_value(cls, value: Any, value_name: str | None = None) -> "ConfigList":
        """Convert given `value` into a `ConfigList` object.

        If `value` is already a `ConfigList` then it is returned as-is.

        Args:
            value: A `ConfigList` object or `list` of items which can be
                converted into `Config` objects including configuration
                names of tyype `str`. The latter are resolved against
                the plugin configurations seen so far in the list.
            value_name: A value's name.
        Returns:
            A `ConfigList` object.
        """
        return super().from_value(value, value_name=value_name)

    @classmethod
    def _from_sequence(cls, value: Sequence, value_name: str) -> "ConfigList":
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
    def _get_value_name(cls) -> str:
        return "config_list"

    @classmethod
    def _get_value_type_name(cls) -> str:
        return "ConfigList | list[Config | dict]"

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
