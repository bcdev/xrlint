from abc import abstractmethod, ABC
from collections.abc import Mapping, Iterable, MutableMapping
from dataclasses import dataclass
from typing import Any, Callable, Type

from xrlint.op import OpMixin, OpMetadata
from xrlint.result import Result
from xrlint.result import ResultStats
from xrlint.util.naming import to_kebab_case


class FormatterContext(ABC):
    """A formatter context is passed to `FormatOp`."""

    @property
    @abstractmethod
    def max_warnings_exceeded(self) -> bool:
        """`True` if the maximum number of warnings has been exceeded."""

    @property
    @abstractmethod
    def result_stats(self) -> ResultStats:
        """Get current result statistics."""


class FormatterOp(ABC):
    """Define the specific format operation."""

    @abstractmethod
    def format(
        self,
        context: FormatterContext,
        results: Iterable[Result],
    ) -> str:
        """Format the given results.

        Args:
            context: formatting context
            results: an iterable of results to format
        Returns:
            A text representing the results in a given format
        """


@dataclass(kw_only=True)
class FormatterMeta(OpMetadata):
    """Formatter metadata."""

    name: str
    """Formatter name."""

    version: str = "0.0.0"
    """Formatter version."""

    ref: str | None = None
    """Formatter reference.
    Specifies the location from where the formatter can be
    dynamically imported.
    Must have the form "<module>:<attr>", if given.
    """

    schema: dict[str, Any] | list[dict[str, Any]] | bool | None = None
    """Formatter options schema."""


@dataclass(frozen=True, kw_only=True)
class Formatter(OpMixin):
    """A formatter for linting results."""

    meta: FormatterMeta
    """The formatter metadata."""

    op_class: Type[FormatterOp]
    """The class that implements the format operation."""

    @classmethod
    @property
    def op_base_class(cls) -> Type:
        return FormatterOp

    @classmethod
    @property
    def op_name(cls) -> str:
        return "formatter"

    @classmethod
    def define(
        cls,
        op_class: Type[FormatterOp] | None = None,
        *,
        registry: MutableMapping[str, "Formatter"] | None = None,
        meta_kwargs: dict[str, Any] | None = None,
        **kwargs,
    ) -> Callable[[FormatterOp], Type[FormatterOp]] | "Formatter":
        return cls._define_op(
            op_class,
            FormatterMeta,
            registry=registry,
            meta_kwargs=meta_kwargs,
            **kwargs,
        )


class FormatterRegistry(Mapping[str, Formatter]):

    def __init__(self):
        self._registrations = {}

    def define_formatter(
        self,
        name: str | None = None,
        version: str | None = None,
        schema: dict[str, Any] | list[dict[str, Any]] | bool | None = None,
    ) -> Callable[[Any], Type[FormatterOp]]:
        return Formatter.define(
            None,
            registry=self._registrations,
            meta_kwargs=dict(name=name, version=version, schema=schema),
        )

    def __getitem__(self, key: str) -> Formatter:
        return self._registrations[key]

    def __len__(self) -> int:
        return len(self._registrations)

    def __iter__(self):
        return iter(self._registrations)
