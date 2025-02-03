#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from functools import cached_property
from typing import TYPE_CHECKING, Any, TypeAlias, Union

from xrlint.constants import CORE_PLUGIN_NAME
from xrlint.util.constructible import MappingConstructible, ValueConstructible
from xrlint.util.filefilter import FileFilter
from xrlint.util.merge import merge_arrays, merge_dicts, merge_set_lists, merge_values
from xrlint.util.serializable import JsonSerializable

if TYPE_CHECKING:  # pragma: no cover
    # make IDEs and flake8 happy
    from xrlint.plugin import Plugin
    from xrlint.processor import ProcessorOp
    from xrlint.rule import Rule, RuleConfig


ConfigObjectLike: TypeAlias = Union[
    "ConfigObject",
    Mapping[str, Any],
    None,
]
"""Type alias for values that can represent configuration objects.
Can be either a [ConfigObject][xrlint.config.ConfigObject] instance,
or a mapping (e.g. `dict`) with properties defined by `ConfigObject`,
or `None` (empty configuration object).
"""

ConfigLike: TypeAlias = Union[
    "Config",
    ConfigObjectLike,
    str,
    Sequence[ConfigObjectLike | str],
]
"""Type alias for values that can represent configurations.
Can be either a [Config][xrlint.config.Config] instance,
or a [configuration object like][xrlint.config.ConfigObjectLike] value,
or a named plugin configuration, or a sequence of the latter two.
"""


def get_core_plugin() -> "Plugin":
    """Get the fully imported, populated core plugin."""
    from xrlint.plugins.core import export_plugin

    return export_plugin()


def get_core_config_object() -> "ConfigObject":
    """Create a configuration object that includes the core plugin.

    Returns:
        A new `Config` object
    """
    return ConfigObject(plugins={CORE_PLUGIN_NAME: get_core_plugin()})


def split_config_spec(config_spec: str) -> tuple[str, str]:
    """Split a configuration specification into plugin name
    and configuration item name.
    """
    return (
        config_spec.split("/", maxsplit=1)
        if "/" in config_spec
        else (CORE_PLUGIN_NAME, config_spec)
    )


@dataclass(frozen=True, kw_only=True)
class ConfigObject(MappingConstructible, JsonSerializable):
    """Configuration object.

    Configuration objects are the items managed by a
    [configuration][xrlint.config.Config].

    You should not use the class constructor directly.
    Instead, use the `ConfigObject.from_value()` function.
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
            or self.processor
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
        from xrlint.processor import Processor, ProcessorOp

        if isinstance(processor_spec, ProcessorOp):
            return processor_spec

        plugin_name, processor_name = split_config_spec(processor_spec)
        plugin = self.get_plugin(plugin_name)
        processor: Processor | None = (plugin.processors or {}).get(processor_name)
        if processor is None:
            raise ValueError(f"unknown processor {processor_spec!r}")
        return processor.op_class()

    def merge(self, config: "ConfigObject", name: str = None) -> "ConfigObject":
        return ConfigObject(
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
    def _from_none(cls, value_name: str) -> "ConfigObject":
        return ConfigObject()

    @classmethod
    def forward_refs(cls) -> dict[str, type]:
        from xrlint.plugin import Plugin
        from xrlint.processor import Processor, ProcessorOp
        from xrlint.rule import Rule, RuleConfig

        return {
            "Processor": Processor,
            "ProcessorOp": ProcessorOp,
            "Plugin": Plugin,
            "Rule": Rule,
            "RuleConfig": RuleConfig,
        }

    @classmethod
    def value_name(cls) -> str:
        return "config_obj"

    @classmethod
    def value_type_name(cls) -> str:
        return "ConfigObject | dict | None"


@dataclass(frozen=True)
class Config(ValueConstructible, JsonSerializable):
    """Represents a XRLint configuration.
    A `Config` instance basically manages a sequence of
    [configuration objects][xrlint.config.ConfigObject].

    You should not use the class constructor directly.
    Instead, use the `Config.from_value()` function.
    """

    objects: list[ConfigObject] = field(default_factory=list)
    """The configuration objects."""

    def split_global_filter(
        self, default: FileFilter | None = None
    ) -> tuple["Config", FileFilter]:
        """Get a global file filter for this configuration list."""
        global_filter = FileFilter(
            default.files if default else (),
            default.ignores if default else (),
        )
        objects = []
        for co in self.objects:
            if co.empty and not co.file_filter.empty:
                global_filter = global_filter.merge(co.file_filter)
            else:
                objects.append(co)
        return Config(objects=objects), global_filter

    def compute_config_object(self, file_path: str) -> ConfigObject | None:
        """Compute the configuration object for the given file path.

        Args:
            file_path: A dataset file path.

        Returns:
            A `Config` object which may be empty, or `None`
                if `file_path` is not included by any `files` pattern
                or intentionally ignored by global `ignores`.
        """

        config_obj = None
        for co in self.objects:
            if co.file_filter.empty or co.file_filter.accept(file_path):
                config_obj = config_obj.merge(co) if config_obj is not None else co

        if config_obj is None:
            return None

        # Note, computed configurations do not have "files" and "ignores"
        return ConfigObject(
            linter_options=config_obj.linter_options,
            opener_options=config_obj.opener_options,
            processor=config_obj.processor,
            plugins=config_obj.plugins,
            rules=config_obj.rules,
            settings=config_obj.settings,
        )

    @classmethod
    def from_config(
        cls,
        *configs: ConfigLike,
        value_name: str | None = None,
    ) -> "Config":
        """Convert variable arguments of configuration-like objects
        into a new `Config` instance.

        Args:
            *configs: Variable number of configuration-like arguments.
                For more information see the
                [ConfigLike][xrlint.config.ConfigLike] type alias.
            value_name: The value's name used for reporting errors.

        Returns:
            A new `Config` instance.
        """
        value_name = value_name or cls.value_name()
        objects: list[ConfigObject] = []
        plugins: dict[str, Plugin] = {}
        for i, config_like in enumerate(configs):
            new_objects = None
            if isinstance(config_like, str):
                if CORE_PLUGIN_NAME not in plugins:
                    plugins.update({CORE_PLUGIN_NAME: get_core_plugin()})
                new_objects = cls._get_named_config(config_like, plugins).objects
            elif isinstance(config_like, Config):
                new_objects = config_like.objects
            elif isinstance(config_like, (list, tuple)):
                new_objects = cls.from_config(
                    *config_like, value_name=f"{value_name}[{i}]"
                ).objects
            elif config_like:
                new_objects = [
                    ConfigObject.from_value(
                        config_like, value_name=f"{value_name}[{i}]"
                    )
                ]
            if new_objects:
                for co in new_objects:
                    objects.append(co)
                    plugins.update(co.plugins if co.plugins else {})
        return cls(objects=objects)

    @classmethod
    def from_value(cls, value: ConfigLike, value_name: str | None = None) -> "Config":
        """Convert given `value` into a `Config` object.

        If `value` is already a `Config` then it is returned as-is.

        Args:
            value: A configuration-like value. For more information
                see the [ConfigLike][xrlint.config.ConfigLike] type alias.
            value_name: The value's name used for reporting errors.
        Returns:
            A `Config` object.
        """
        if isinstance(value, (ConfigObject, dict)):
            return Config(objects=[ConfigObject.from_value(value)])
        return super().from_value(value, value_name=value_name)

    @classmethod
    def _from_sequence(cls, value: Sequence, value_name: str) -> "Config":
        return cls.from_config(*value, value_name=value_name)

    @classmethod
    def value_name(cls) -> str:
        return "config"

    @classmethod
    def value_type_name(cls) -> str:
        return "Config | ConfigObjectLike | str | Sequence[ConfigObjectLike | str]"

    @classmethod
    def _get_named_config(
        cls, config_spec: str, plugins: dict[str, "Plugin"]
    ) -> "Config":
        plugin_name, config_name = (
            config_spec.split("/", maxsplit=1)
            if "/" in config_spec
            else (CORE_PLUGIN_NAME, config_spec)
        )
        plugin: Plugin | None = plugins.get(plugin_name)
        if plugin is None or not plugin.configs or config_name not in plugin.configs:
            raise ValueError(f"configuration {config_spec!r} not found")
        return Config.from_value(plugin.configs[config_name])
