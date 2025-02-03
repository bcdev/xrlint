#  Copyright © 2025 Brockmann Consult GmbH.
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
    "XRLint",
    "Config",
    "ConfigLike",
    "ConfigObject",
    "ConfigObjectLike",
    "Linter",
    "new_linter",
    "EditInfo",
    "Message",
    "Result",
    "Suggestion",
    "get_rules_meta_for_results",
    "Formatter",
    "FormatterContext",
    "FormatterMeta",
    "FormatterOp",
    "FormatterRegistry",
    "AttrNode",
    "AttrsNode",
    "VariableNode",
    "DatasetNode",
    "Node",
    "Plugin",
    "PluginMeta",
    "new_plugin",
    "Processor",
    "ProcessorMeta",
    "ProcessorOp",
    "define_processor",
    "Rule",
    "RuleConfig",
    "RuleContext",
    "RuleExit",
    "RuleMeta",
    "RuleOp",
    "define_rule",
    "RuleTest",
    "RuleTester",
    "version",
]
