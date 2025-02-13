#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from abc import ABC, abstractmethod
from collections.abc import MutableMapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Callable, Literal, Type

import xarray as xr

from xrlint.constants import SEVERITY_ENUM, SEVERITY_ENUM_TEXT
from xrlint.node import AttrNode, AttrsNode, DatasetNode, DataTreeNode, VariableNode
from xrlint.operation import Operation, OperationMeta
from xrlint.result import Suggestion
from xrlint.util.constructible import ValueConstructible
from xrlint.util.formatting import format_message_one_of
from xrlint.util.serializable import JsonSerializable


class RuleContext(ABC):
    """The context passed to a [RuleOp][xrlint.rule.RuleOp] instance.

    Instances of this interface are passed to the validation
    methods of your `RuleOp`.
    There should be no reason to create instances of this class
    yourself.
    """

    @property
    @abstractmethod
    def file_path(self) -> str:
        """The current dataset's file path."""

    @property
    @abstractmethod
    def settings(self) -> dict[str, Any]:
        """Applicable subset of settings from configuration `settings`."""

    @property
    @abstractmethod
    def dataset(self) -> xr.Dataset:
        """The current dataset."""

    @property
    @abstractmethod
    def access_latency(self) -> float | None:
        """The time in seconds that it took for opening the dataset.
        `None` if the dataset has not been opened from `file_path`.
        """

    @abstractmethod
    def report(
        self,
        message: str,
        *,
        fatal: bool | None = None,
        suggestions: list[Suggestion | str] | None = None,
    ):
        """Report an issue.

        Args:
            message: mandatory message text
            fatal: True, if a fatal error is reported.
            suggestions: A list of suggestions for the user
                on how to fix the reported issue. Items may
                be of type `Suggestion` or `str`.
        """


class RuleExit(Exception):
    """The `RuleExit` is an exception that can be raised to
    immediately cancel dataset node validation with the current rule.

    Raise it from any of your `RuleOp` method implementations if further
    node traversal doesn't make sense. Typical usage:

    ```python
    if something_is_not_ok:
        ctx.report("Something is not ok.")
        raise RuleExit
    ```
    """


class RuleOp(ABC):
    """Define the specific rule validation operations."""

    def validate_datatree(self, ctx: RuleContext, node: DataTreeNode) -> None:
        """Validate the given datatree node.

        Args:
            ctx: The current rule context.
            node: The datatree node.

        Raises:
            RuleExit: to exit rule logic and further node traversal
        """

    def validate_dataset(self, ctx: RuleContext, node: DatasetNode) -> None:
        """Validate the given dataset node.

        Args:
            ctx: The current rule context.
            node: The dataset node.

        Raises:
            RuleExit: to exit rule logic and further node traversal
        """

    def validate_variable(self, ctx: RuleContext, node: VariableNode) -> None:
        """Validate the given data array (variable) node.

        Args:
            ctx: The current rule context.
            node: The data array (variable) node.

        Raises:
            RuleExit: to exit rule logic and further node traversal
        """

    def validate_attrs(self, ctx: RuleContext, node: AttrsNode) -> None:
        """Validate the given attributes node.

        Args:
            ctx: The current rule context.
            node: The attributes node.

        Raises:
            RuleExit: to exit rule logic and further node traversal
        """

    def validate_attr(self, ctx: RuleContext, node: AttrNode) -> None:
        """Validate the given attribute node.

        Args:
            ctx: The current rule context.
            node: The attribute node.

        Raises:
            RuleExit: to exit rule logic and further node traversal
        """


@dataclass(kw_only=True)
class RuleMeta(OperationMeta):
    """Rule metadata."""

    name: str
    """Rule name. Mandatory."""

    version: str = "0.0.0"
    """Rule version. Defaults to `0.0.0`."""

    description: str | None = None
    """Rule description."""

    docs_url: str | None = None
    """Rule documentation URL."""

    schema: dict[str, Any] | list[dict[str, Any]] | bool | None = None
    """JSON Schema used to specify and validate the rule operation
    options.

    It can take the following values:

    - Use `None` (the default) to indicate that the rule operation
      as no options at all.
    - Use a schema to indicate that the rule operation
      takes keyword arguments only.
      The schema's type must be `"object"`.
    - Use a list of schemas to indicate that the rule operation
      takes positional arguments only.
      If given, the number of schemas in the list specifies the
      number of positional arguments that must be configured.
    """

    type: Literal["problem", "suggestion", "layout"] = "problem"
    """Rule type. Defaults to `"problem"`.

    The type field can have one of the following values:

    - `"problem"`: Indicates that the rule addresses datasets that are
      likely to cause errors or unexpected behavior during runtime.
      These issues usually represent real bugs or potential runtime problems.
    - `"suggestion"`: Used for rules that suggest structural improvements
      or enforce best practices. These issues are not necessarily bugs, but
      following the suggestions may lead to more readable, maintainable, or
      consistent datasets.
    - `"layout"`: Specifies that the rule enforces consistent stylistic
      aspects of dataset formatting, e.g., whitespaces in names.
      Issues with layout rules are often automatically fixable
      (not supported yet).

    Primarily serves to categorize the rule's purpose for the benefit
    of developers and tools that consume XRLint output.
    It doesn’t directly affect the linting logic - that part is handled
    by the rule’s implementation and its configured severity.
    """

    @classmethod
    def value_name(cls) -> str:
        return "rule_meta"

    @classmethod
    def value_type_name(cls) -> str:
        return "RuleMeta | dict"


@dataclass(frozen=True)
class Rule(Operation):
    """A rule comprises rule metadata and a reference to the
    class that implements the rule's logic.

    Instances of this class can be easily created and added to a plugin
    by using the decorator `@define_rule` of the `Plugin` class.

    Args:
        meta: the rule's metadata
        op_class: the class that implements the rule's logic
    """

    meta: RuleMeta
    """Rule metadata of type `RuleMeta`."""

    op_class: Type[RuleOp]
    """The class the implements the rule's validation operation.
    The class must implement the `RuleOp` interface.
    """

    @classmethod
    def meta_class(cls) -> Type:
        return RuleMeta

    @classmethod
    def op_base_class(cls) -> Type:
        return RuleOp

    @classmethod
    def value_name(cls) -> str:
        return "rule"


@dataclass(frozen=True)
class RuleConfig(ValueConstructible, JsonSerializable):
    """A rule configuration.

    You should not use the class constructor directly.
    Instead, use its [from_value][xrlint.rule.RuleConfig.from_value]
    class method. The method's argument value can either be a
    rule _severity_, or a list where the first element is a rule
    _severity_ and subsequent elements are rule arguments:

    - _severity_
    - `[`_severity_`]`
    - `[`_severity_`,` _arg-1 | kwargs_ `]`
    - `[`_severity_`,` _arg-1_`,` _arg-2_`,` ...`,` _arg-n | kwargs_`]`

    The rule _severity_ is either

    - one of `"error"`, `"warn"`, `"off"` or
    - one of `2` (error), `1` (warn), `0` (off)

    Args:
        severity: rule severity, one of `2` (error), `1` (warn), or `0` (off)
        args: rule operation arguments.
        kwargs: rule operation keyword-arguments.
    """

    severity: Literal[0, 1, 2]
    """Rule severity, one of `2` (error), `1` (warn), or `0` (off)."""

    args: tuple[Any, ...] = field(default_factory=tuple)
    """Rule operation arguments."""

    kwargs: dict[str, Any] = field(default_factory=dict)
    """Rule operation keyword-arguments."""

    @classmethod
    def _convert_severity(cls, value: int | str) -> Literal[2, 1, 0]:
        try:
            # noinspection PyTypeChecker
            return SEVERITY_ENUM[value]
        except KeyError:
            raise ValueError(
                format_message_one_of("severity", value, SEVERITY_ENUM_TEXT)
            )

    @classmethod
    def _from_bool(cls, value: bool, name: str) -> "RuleConfig":
        return RuleConfig(cls._convert_severity(int(value)))

    @classmethod
    def _from_int(cls, value: int, name: str) -> "RuleConfig":
        return RuleConfig(cls._convert_severity(value))

    @classmethod
    def _from_str(cls, value: str, value_name: str) -> "RuleConfig":
        return RuleConfig(cls._convert_severity(value))

    @classmethod
    def _from_sequence(cls, value: Sequence, value_name: str) -> "RuleConfig":
        if not value:
            raise ValueError(f"{value_name} must not be empty")
        severity = cls._convert_severity(value[0])
        options = value[1:]
        if not options:
            args, kwargs = (), {}
        elif isinstance(options[-1], dict):
            args, kwargs = options[:-1], options[-1]
        else:
            args, kwargs = options, {}
        # noinspection PyTypeChecker
        return RuleConfig(severity, tuple(args), dict(kwargs))

    @classmethod
    def value_name(cls) -> str:
        return "rule_config"

    @classmethod
    def value_type_name(cls) -> str:
        return "int | str | list"

    # noinspection PyUnusedLocal
    def to_json(self, value_name: str | None = None) -> int | list:
        if not self.args and not self.kwargs:
            return self.severity
        else:
            return [self.severity, *self.args, self.kwargs]


def define_rule(
    name: str | None = None,
    version: str = "0.0.0",
    type: Literal["problem", "suggestion", "layout"] = "problem",
    description: str | None = None,
    docs_url: str | None = None,
    schema: dict[str, Any] | list[dict[str, Any]] | bool | None = None,
    registry: MutableMapping[str, Rule] | None = None,
    op_class: Type[RuleOp] | None = None,
) -> Callable[[Any], Type[RuleOp]] | Rule:
    """Define a rule.

    This function can be used to decorate your rule operation class
    definitions. When used as a decorator, the decorated operator class
    will receive a `meta` attribute of type [RuleMeta][xrlint.rule.RuleMeta].
    In addition, the `registry` if given, will be updated using `name`
    as key and a new [Rule][xrlint.rule.Rule] as value.

    Args:
        name: Rule name, see [RuleMeta][xrlint.rule.RuleMeta].
        version: Rule version, see [RuleMeta][xrlint.rule.RuleMeta].
        type: Rule type, see [RuleMeta][xrlint.rule.RuleMeta].
        description: Rule description,
            see [RuleMeta][xrlint.rule.RuleMeta].
        docs_url: Rule documentation URL,
            see [RuleMeta][xrlint.rule.RuleMeta].
        schema: Rule operation arguments schema,
            see [RuleMeta][xrlint.rule.RuleMeta].
        registry: Rule registry. Can be provided to register the
            defined rule using its `name`.
        op_class: Rule operation class. Must not be provided
            if this function is used as a class decorator.

    Returns:
        A decorator function, if `op_class` is `None` otherwise
            the value of `op_class`.

    Raises:
        TypeError: If either `op_class` or the decorated object is not
            a class derived from [RuleOp][xrlint.rule.RuleOp].
    """
    return Rule.define_operation(
        op_class,
        registry=registry,
        meta_kwargs=dict(
            name=name,
            version=version,
            description=description,
            docs_url=docs_url,
            type=type if type else "problem",
            schema=schema,
        ),
    )
