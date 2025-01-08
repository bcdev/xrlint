from abc import abstractmethod, ABC
from dataclasses import dataclass, field
from typing import Type, Literal, Any, Callable

import xarray as xr

from xrlint.constants import SEVERITY_ENUM, SEVERITY_ENUM_TEXT
from xrlint.node import DatasetNode, DataArrayNode, AttrsNode, AttrNode
from xrlint.result import Suggestion
from xrlint.util.formatting import format_message_type_of, format_message_one_of
from xrlint.util.todict import ToDictMixin


class RuleContext(ABC):
    """The context passed to the verifier of a rule.

    You should never create instances of this class yourself.
    Instances of this interface are passed to the `RuleOp`'s
    methods.
    """

    @property
    @abstractmethod
    def settings(self) -> dict[str, Any]:
        """Configuration settings."""

    @property
    @abstractmethod
    def dataset(self) -> xr.Dataset:
        """Get the current dataset."""

    @property
    @abstractmethod
    def file_path(self) -> str:
        """Get the current dataset's file path."""

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
    """Define the specific rule verification operation."""

    def dataset(self, context: RuleContext, node: DatasetNode) -> None:
        """Verify the given dataset node.

        Args:
            context: The current rule context.
            node: The dataset node.
        Raises:
            RuleExit: to exit rule logic and further node traversal
        """

    def data_array(self, context: RuleContext, node: DataArrayNode) -> None:
        """Verify the given data array (variable) node.

        Args:
            context: The current rule context.
            node: The data array (variable) node.
        Raises:
            RuleExit: to exit rule logic and further node traversal
        """

    def attrs(self, context: RuleContext, node: AttrsNode) -> None:
        """Verify the given attributes node.

        Args:
            context: The current rule context.
            node: The attributes node.
        Raises:
            RuleExit: to exit rule logic and further node traversal
        """

    def attr(self, context: RuleContext, node: AttrNode) -> None:
        """Verify the given attribute node.

        Args:
            context: The current rule context.
            node: The attribute node.
        Raises:
            RuleExit: to exit rule logic and further node traversal
        """


@dataclass(frozen=True, kw_only=True)
class RuleMeta(ToDictMixin):
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
    """JSON Schema used to specify and validate the rule verifier's
    options.

    It can take the following values:

    - Use `None` (the default) to indicate that the rule verifier
      as no options at all.
    - Use a schema to indicate that the rule verifier
      takes keyword arguments only.
      The schema's type must be `"object"`.
    - Use a list of schemas to indicate that the rule verifier
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


@dataclass(frozen=True)
class Rule:
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
    """The class the implements the rule's verification operation.
    The class must implement the `RuleOp` interface.
    """


@dataclass(frozen=True)
class RuleConfig:
    """A rule configuration.

    You should not use the class constructor directly.
    Instead, use the `RuleConfig.from_value()` function.

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
    def from_value(cls, value: Any) -> "RuleConfig":
        """Convert `value` into a `RuleConfig` object.

        A rule configuration value can either be a rule _severity_,
        or a list where the first element is a rule
        _severity_ and subsequent elements are rule arguments:

        - _severity_
        - `[`_severity_`]`
        - `[`_severity_`,` _arg-1 | kwargs_ `]`
        - `[`_severity_`,` _arg-1_`,` _arg-2_`,` ...`,` _arg-n | kwargs_`]`

        The rule _severity_ is either

        - one of `"error"`, `"warn"`, `"off"` or
        - one of `2` (error), `1` (warn), `0` (off)

        Args:
            value: A rule severity or a list where the first element is a rule
                severity and subsequent elements are rule arguments.
                If the value is already of type `RuleConfig`it is returned as-is.
        Returns:
            A `RuleConfig` object.
        """
        if isinstance(value, RuleConfig):
            return value

        if isinstance(value, (int, str)):
            severity_value, options = value, ()
        elif isinstance(value, (list, tuple)):
            severity_value, options = (value[0], value[1:]) if value else (0, ())
        else:
            raise TypeError(
                format_message_type_of(
                    "rule configuration", value, "int|str|tuple|list"
                )
            )

        try:
            severity = SEVERITY_ENUM[severity_value]
        except KeyError:
            raise ValueError(
                format_message_one_of("severity", severity_value, SEVERITY_ENUM_TEXT)
            )

        if not options:
            args, kwargs = (), {}
        elif isinstance(options[-1], dict):
            args, kwargs = options[:-1], options[-1]
        else:
            args, kwargs = options, {}

        # noinspection PyTypeChecker
        return RuleConfig(severity, tuple(args), dict(kwargs))


def register_rule(
    registry: dict[str, Rule],
    name: str,
    version: str = "0.0.0",
    schema: dict[str, Any] | list[dict[str, Any]] | bool | None = None,
    type: Literal["problem", "suggestion", "layout"] | None = None,
    description: str | None = None,
    docs_url: str | None = None,
    op_class: Type[RuleOp] | None = None,
) -> Callable[[Any], Type[RuleOp]] | None:
    def _register_rule(_op_class: Any) -> Type[RuleOp]:
        from inspect import isclass

        if not isclass(_op_class) or not issubclass(_op_class, RuleOp):
            raise TypeError(
                f"component decorated by define_rule()"
                f" must be a subclass of {RuleOp.__name__}"
            )
        meta = RuleMeta(
            name=name,
            version=version,
            description=description,
            docs_url=docs_url,
            type=type if type is not None else "problem",
            schema=schema,
        )
        registry[name] = Rule(meta=meta, op_class=_op_class)
        return _op_class

    if op_class is None:
        # decorator case
        return _register_rule

    _register_rule(op_class)
