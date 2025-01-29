import re

from xrlint.node import DataArrayNode, DatasetNode
from xrlint.plugins.core.plugin import plugin
from xrlint.rule import RuleContext, RuleOp
from xrlint.util.schema import schema

DEFAULT_GLOBAL_ATTRS = ["title", "history"]
DEFAULT_VAR_ATTRS = ["institution", "source", "references", "comment"]
DEFAULT_IGNORES = ["crs", "spatial_ref"]


@plugin.define_rule(
    "dataset-description",
    version="1.0.0",
    type="suggestion",
    description=(
        "A dataset should provide information about where the data came"
        " from and what has been done to it."
        " This information is mainly for the benefit of human readers."
        " The rule accepts the following configuration parameters:\n\n"
        "- `global_attrs`: list of global attribute names."
        f" Defaults to `{DEFAULT_GLOBAL_ATTRS}`.\n"
        "- `var_attrs`: list of variable attribute names."
        f" Defaults to `{DEFAULT_VAR_ATTRS}`.\n"
        "- `ignored_vars`: list of ignored variables (regex patterns)."
        f" Defaults to `{DEFAULT_IGNORES}`.\n"
        ""
    ),
    docs_url=(
        "https://cfconventions.org/cf-conventions/cf-conventions.html"
        "#description-of-file-contents"
    ),
    schema=schema(
        "object",
        properties={
            "global_attrs": schema(
                "array",
                items=schema("string"),
                default=DEFAULT_GLOBAL_ATTRS,
                title="Global dataset attribute names",
            ),
            "var_attrs": schema(
                "array",
                items=schema("string"),
                default=DEFAULT_VAR_ATTRS,
                title="Data variable attribute names",
            ),
            "ignored_vars": schema(
                "array",
                items=schema("string"),
                default=DEFAULT_IGNORES,
                title="Ignored variables (regex name patterns)",
            ),
        },
    ),
)
class DatasetDescription(RuleOp):
    def __init__(
        self, global_attrs: list[str] | None = None, var_attrs: list[str] | None = None
    ):
        self.global_attrs = global_attrs if global_attrs else DEFAULT_GLOBAL_ATTRS
        self.var_attrs = var_attrs if var_attrs else DEFAULT_VAR_ATTRS
        self.ignored_vars = [
            re.compile(p) for p in (var_attrs if var_attrs else DEFAULT_VAR_ATTRS)
        ]

    def dataset(self, ctx: RuleContext, node: DatasetNode):
        dataset = node.dataset
        for attr_name in self.global_attrs:
            if attr_name not in dataset.attrs:
                ctx.report(f"Missing dataset attribute {attr_name!r}.")

    def data_array(self, ctx: RuleContext, node: DataArrayNode):
        dataset = ctx.dataset
        if node.name not in dataset.data_vars:
            return

        for m in self.ignored_vars:
            if m.match(str(node.name)):
                return

        var = node.data_array
        for attr_name in self.var_attrs:
            if attr_name not in var.attrs and attr_name not in dataset.attrs:
                ctx.report(f"Missing data variable attribute {attr_name!r}.")
