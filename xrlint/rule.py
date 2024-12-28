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
    """The context passed to the verifier of a rule."""

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
        suggestions: list[Suggestion] | None = None,
    ):
        """Report an issue.

        Args:
            message: mandatory message text
            fatal: True, if a fatal error is reported.
            suggestions: A list of suggestions for the user
                on how to fix the reported issue.
        """


class RuleOp:
    """Define the specific rule verification operation."""

    def dataset(self, ctx: RuleContext, node: DatasetNode):
        """Verify the given node."""

    def data_array(self, ctx: RuleContext, node: DataArrayNode):
        """Verify the given node."""

    def attrs(self, ctx: RuleContext, node: AttrsNode):
        """Verify the given node."""

    def attr(self, ctx: RuleContext, node: AttrNode):
        """Verify the given node."""


@dataclass(frozen=True, kw_only=True)
class RuleMeta(ToDictMixin):
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

    type: Literal["problem", "suggestion"] = "problem"
    """Rule type. Defaults to `"problem"`."""


@dataclass(frozen=True)
class Rule:
    """A rule."""

    meta: RuleMeta
    """Rule metadata of type `RuleMeta`."""

    op_class: Type[RuleOp]
    """The class of the rule verifier.
    Must implement the `RuleVerifier` interface. 
    """


@dataclass(frozen=True)
class RuleConfig:
    """Rule configuration.

    Args:
        severity: 0, 1, 2

    """

    severity: Literal[0, 1, 2]
    args: tuple[Any, ...] = field(default_factory=tuple)
    kwargs: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_value(cls, value: Any) -> "RuleConfig":
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
    /,
    version: str | None = None,
    schema: dict[str, Any] | list[dict[str, Any]] | bool | None = None,
    type: Literal["problem", "suggestion"] | None = None,
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
