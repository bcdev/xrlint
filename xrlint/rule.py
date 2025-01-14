from abc import abstractmethod, ABC
from collections.abc import MutableMapping, Sequence
from dataclasses import dataclass, field
from inspect import isclass
from typing import Type, Literal, Any, Callable

import xarray as xr

from xrlint.constants import (
    SEVERITY_ENUM,
    SEVERITY_ENUM_TEXT,
)
from xrlint.node import DatasetNode, DataArrayNode, AttrsNode, AttrNode
from xrlint.result import Suggestion
from xrlint.util.codec import (
    MappingConstructible,
    ValueConstructible,
    JsonSerializable,
)
from xrlint.util.formatting import format_message_one_of
from xrlint.util.importutil import import_value
from xrlint.util.naming import to_kebab_case


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


@dataclass(kw_only=True)
class RuleMeta(MappingConstructible, JsonSerializable):
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

    ref: str | None = None
    """Rule reference.
    Specifies the location from where the rule can be
    dynamically imported.
    Must have the form "<module>:<attr>", if given.
    """

    @classmethod
    def _get_value_type_name(cls) -> str:
        return "RuleMeta | dict"

    def to_dict(self, value_name: str | None = None) -> dict[str, str]:
        return {
            k: v
            for k, v in super().to_dict(value_name=value_name).items()
            if v is not None
        }


@dataclass(frozen=True)
class Rule(MappingConstructible, JsonSerializable):
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

    @classmethod
    def _from_str(cls, value: str, value_name: str) -> "Rule":
        rule, rule_ref = import_value(value, "export_rule", factory=Rule.from_value)
        rule.meta.ref = rule_ref
        return rule

    @classmethod
    def _from_type(cls, value: Type, value_name: str) -> "Rule":
        if issubclass(value, RuleOp):
            op_class = value
            try:
                # noinspection PyUnresolvedReferences
                # Note, the value.meta attribute is set by
                # the define_rule() function.
                meta = value.meta
            except AttributeError:
                raise ValueError(
                    f"missing rule metadata, apply define_rule()"
                    f" to class {value.__name__}"
                )
            return Rule(meta=meta, op_class=op_class)
        super()._from_type(value, value_name)

    @classmethod
    def _get_value_type_name(cls) -> str:
        return "Rule | dict | str"

    # noinspection PyUnusedLocal
    def to_json(self, value_name: str | None = None) -> str:
        if self.meta.ref:
            return self.meta.ref
        return super().to_json(value_name=value_name)


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
    def _get_value_name(cls) -> str:
        return "rule configuration"

    @classmethod
    def _get_value_type_name(cls) -> str:
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
    schema: dict[str, Any] | list[dict[str, Any]] | bool | None = None,
    type: Literal["problem", "suggestion", "layout"] | None = None,
    description: str | None = None,
    docs_url: str | None = None,
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
        schema: Rule operation arguments schema,
            see [RuleMeta][xrlint.rule.RuleMeta].
        type: Rule type, see [RuleMeta][xrlint.rule.RuleMeta].
        description: Rule description,
            see [RuleMeta][xrlint.rule.RuleMeta].
        docs_url: Rule documentation URL,
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

    def _define_rule(_op_class: Type[RuleOp], no_deco=False) -> Type[RuleOp] | Rule:
        if not isclass(_op_class) or not issubclass(_op_class, RuleOp):
            raise TypeError(
                f"component decorated by define_rule()"
                f" must be a subclass of {RuleOp.__name__}"
            )
        meta = RuleMeta(
            name=name or to_kebab_case(_op_class.__name__),
            version=version,
            description=description or _op_class.__doc__,
            docs_url=docs_url,
            type=type if type is not None else "problem",
            # TODO: if schema not given,
            #   derive it from _op_class' ctor arguments
            schema=schema,
        )
        # Register rule metadata in rule operation class
        setattr(_op_class, "meta", meta)
        rule = Rule(meta=meta, op_class=_op_class)
        if registry is not None:
            # Register rule in rule registry
            registry[meta.name] = rule
        return rule if no_deco else _op_class

    if op_class is None:
        # decorator case: return decorated class
        return _define_rule
    else:
        # called as function: return new rule
        return _define_rule(op_class, no_deco=True)
