#  Copyright © 2025-2026 Brockmann Consult GmbH and contributors.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from xrlint.cli.engine import XRLint
from xrlint.config import Config, ConfigLike, ConfigObject, ConfigObjectLike
from xrlint.formatter import (
    Formatter,
    FormatterContext,
    FormatterMeta,
    FormatterOp,
    FormatterRegistry,
)
from xrlint.linter import Linter, new_linter
from xrlint.node import AttrNode, AttrsNode, DatasetNode, Node, VariableNode
from xrlint.plugin import Plugin, PluginMeta, new_plugin
from xrlint.processor import Processor, ProcessorMeta, ProcessorOp, define_processor
from xrlint.result import (
    EditInfo,
    Message,
    Result,
    Suggestion,
    get_rules_meta_for_results,
)
from xrlint.rule import (
    Rule,
    RuleConfig,
    RuleContext,
    RuleExit,
    RuleMeta,
    RuleOp,
    define_rule,
)
from xrlint.testing import RuleTest, RuleTester
from xrlint.version import version

__all__ = [
    "AttrNode",
    "AttrsNode",
    "Config",
    "ConfigLike",
    "ConfigObject",
    "ConfigObjectLike",
    "DatasetNode",
    "EditInfo",
    "Formatter",
    "FormatterContext",
    "FormatterMeta",
    "FormatterOp",
    "FormatterRegistry",
    "Linter",
    "Message",
    "Node",
    "Plugin",
    "PluginMeta",
    "Processor",
    "ProcessorMeta",
    "ProcessorOp",
    "Result",
    "Rule",
    "RuleConfig",
    "RuleContext",
    "RuleExit",
    "RuleMeta",
    "RuleOp",
    "RuleTest",
    "RuleTester",
    "Suggestion",
    "VariableNode",
    "XRLint",
    "define_processor",
    "define_rule",
    "get_rules_meta_for_results",
    "new_linter",
    "new_plugin",
    "version",
]
