# noinspection PyUnresolvedReferences
from xrlint.cli.engine import CliEngine

# noinspection PyUnresolvedReferences
from xrlint.config import Config

# noinspection PyUnresolvedReferences
from xrlint.config import ConfigList

# noinspection PyUnresolvedReferences
from xrlint.formatter import Formatter

# noinspection PyUnresolvedReferences
from xrlint.formatter import FormatterMeta

# noinspection PyUnresolvedReferences
from xrlint.formatter import FormatterContext

# noinspection PyUnresolvedReferences
from xrlint.formatter import FormatterOp

# noinspection PyUnresolvedReferences
from xrlint.formatter import FormatterRegistry

# noinspection PyUnresolvedReferences
from xrlint.formatters import export_formatters

# noinspection PyUnresolvedReferences
from xrlint.linter import Linter

# noinspection PyUnresolvedReferences
from xrlint.result import Message

# noinspection PyUnresolvedReferences
from xrlint.result import Suggestion

# noinspection PyUnresolvedReferences
from xrlint.result import EditInfo

# noinspection PyUnresolvedReferences
from xrlint.result import Result

# noinspection PyUnresolvedReferences
from xrlint.result import get_rules_meta_for_results

# noinspection PyUnresolvedReferences
from xrlint.node import AttrsNode

# noinspection PyUnresolvedReferences
from xrlint.node import AttrNode

# noinspection PyUnresolvedReferences
from xrlint.node import DatasetNode

# noinspection PyUnresolvedReferences
from xrlint.node import DataArrayNode

# noinspection PyUnresolvedReferences
from xrlint.node import Node

# noinspection PyUnresolvedReferences
from xrlint.plugin import Plugin

# noinspection PyUnresolvedReferences
from xrlint.plugin import PluginMeta

# noinspection PyUnresolvedReferences
from xrlint.processor import Processor

# noinspection PyUnresolvedReferences
from xrlint.processor import ProcessorMeta

# noinspection PyUnresolvedReferences
from xrlint.processor import ProcessorOp

# noinspection PyUnresolvedReferences
from xrlint.rule import Rule

# noinspection PyUnresolvedReferences
from xrlint.rule import RuleConfig

# noinspection PyUnresolvedReferences
from xrlint.rule import RuleContext

# noinspection PyUnresolvedReferences
from xrlint.rule import RuleMeta

# noinspection PyUnresolvedReferences
from xrlint.rule import RuleOp

# noinspection PyUnresolvedReferences
from xrlint.testing import RuleTest

# noinspection PyUnresolvedReferences
from xrlint.testing import RuleTester

# noinspection PyUnresolvedReferences
from xrlint.version import version

###################################################################

# noinspection PyUnresolvedReferences
from xrlint.plugins.core import export_plugin as import_core_plugin

# noinspection PyUnresolvedReferences
from xrlint.plugins.xcube import export_plugin as import_xcube_plugin

# noinspection PyUnresolvedReferences
from xrlint.formatters import export_formatters as import_formatters

core_plugin = import_core_plugin()
xcube_plugin = import_xcube_plugin()
formatters = import_formatters()

del import_core_plugin
del import_xcube_plugin
del import_formatters
del export_formatters


def new_linter(
    recommended: bool = True, config: Config | dict | None = None, **config_kwargs
) -> Linter:
    """Create a new `Linter` with all built-in plugins configured.

    Args:
        recommended: `True` (the default) if the recommended rule configurations of
            the built-in plugins should be used.
            If set to `False`, you should configure the `rules` option either
            in `config` or `config_kwargs`. Otherwise, calling `verify_dataset()`
            will never succeed for any given dataset.
        config: The `config` keyword argument passed to the `Linter` class
        config_kwargs: The `config_kwargs` keyword arguments passed to the `Linter` class
    Returns:
        A new linter instance
    """
    from xrlint.constants import CORE_PLUGIN_NAME
    from xrlint.config import merge_configs

    base_config = Config(
        plugins={
            CORE_PLUGIN_NAME: core_plugin,
            "xcube": xcube_plugin,
        },
        rules=(
            {
                **core_plugin.configs["recommended"].rules,
                **xcube_plugin.configs["xcube-recommended"].rules,
            }
            if recommended
            else None
        ),
    )

    return Linter(config=merge_configs(base_config, config), **config_kwargs)
