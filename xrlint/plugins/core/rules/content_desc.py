#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

import re

from xrlint.node import DatasetNode, VariableNode
from xrlint.plugins.core.plugin import plugin
from xrlint.rule import RuleContext, RuleExit, RuleOp
from xrlint.util.schema import schema

DEFAULT_GLOBAL_ATTRS = ["title", "history"]
DEFAULT_COMMON_ATTRS = ["institution", "source", "references", "comment"]
DEFAULT_SKIP_VARS = False
# for the case that these are data vars by accident
DEFAULT_IGNORED_VARS = ["crs", "spatial_ref"]


@plugin.define_rule(
    "content-desc",
    version="1.0.0",
    type="suggestion",
    description=(
        "A dataset should provide information about where the data came"
        " from and what has been done to it."
        " This information is mainly for the benefit of human readers."
        " The rule accepts the following configuration parameters:\n\n"
        "- `globals`: list of names of required global attributes."
        f" Defaults to `{DEFAULT_GLOBAL_ATTRS}`.\n"
        "- `commons`: list of names of required variable attributes"
        " that can also be defined globally."
        f" Defaults to `{DEFAULT_COMMON_ATTRS}`.\n"
        "- `no_vars`: do not check variables at all."
        f" Defaults to `{DEFAULT_SKIP_VARS}`.\n"
        "- `ignored_vars`: list of ignored variables (regex patterns)."
        f" Defaults to `{DEFAULT_IGNORED_VARS}`.\n"
        ""
    ),
    docs_url=(
        "https://cfconventions.org/cf-conventions/cf-conventions.html"
        "#description-of-file-contents"
    ),
    schema=schema(
        "object",
        properties={
            "globals": schema(
                "array",
                items=schema("string"),
                default=DEFAULT_GLOBAL_ATTRS,
                title="Global attribute names",
            ),
            "commons": schema(
                "array",
                items=schema("string"),
                default=DEFAULT_COMMON_ATTRS,
                title="Common attribute names",
            ),
            "skip_vars": schema(
                "boolean",
                default=DEFAULT_SKIP_VARS,
                title="Do not check variables",
            ),
            "ignored_vars": schema(
                "array",
                items=schema("string"),
                default=DEFAULT_IGNORED_VARS,
                title="Ignored variables (regex name patterns)",
            ),
        },
    ),
)
class ContentDesc(RuleOp):
    def __init__(self, **params):
        self.global_attrs = params.get("globals", DEFAULT_GLOBAL_ATTRS)
        self.common_attrs = params.get("commons", DEFAULT_COMMON_ATTRS)
        self.skip_vars = params.get("skip_vars", DEFAULT_SKIP_VARS)
        self.ignored_vars = [
            re.compile(p) for p in params.get("ignored_vars", DEFAULT_IGNORED_VARS)
        ]

    def validate_dataset(self, ctx: RuleContext, node: DatasetNode):
        dataset_attrs = node.dataset.attrs
        attr_names = (
            self.global_attrs + self.common_attrs
            if self.skip_vars
            else self.global_attrs
        )
        for attr_name in attr_names:
            if attr_name not in dataset_attrs:
                ctx.report(f"Missing attribute {attr_name!r}.")

    def validate_variable(self, ctx: RuleContext, node: VariableNode):
        if self.skip_vars:
            # Since dataset() has already been processed,
            # no need to check other nodes.
            raise RuleExit

        if node.name not in ctx.dataset.data_vars:
            # Not a data variable
            return

        for m in self.ignored_vars:
            if m.match(str(node.name)):
                # Ignored variable
                return

        var_attrs = node.array.attrs
        dataset_attrs = ctx.dataset.attrs
        for attr_name in self.common_attrs:
            if attr_name not in var_attrs and attr_name not in dataset_attrs:
                ctx.report(f"Missing attribute {attr_name!r}.")
