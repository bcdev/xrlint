from abc import abstractmethod, ABC
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Callable, Type

from xrlint.result import Result
from xrlint.util.naming import to_kebab_case


class FormatterContext:
    """A formatter context is passed to `FormatOp`."""

    def __init__(self, max_warnings_exceeded: bool = False):
        self.max_warnings_exceeded = max_warnings_exceeded
        """`True` if the maximum number of results has been exceeded."""


class FormatterOp(ABC):
    """Define the specific format operation."""

    @abstractmethod
    def format(
        self,
        context: FormatterContext,
        results: list[Result],
    ) -> str:
        """Format the given results.

        Args:
            context: formatting context
            results: the results to format
        Returns:
            A text representing the results in a given format
        """


@dataclass(frozen=True, kw_only=True)
class FormatterMeta:
    """Formatter metadata."""

    name: str
    """Formatter name."""
    version: str = "0.0.0"
    """Formatter version."""
    schema: dict[str, Any] | list[dict[str, Any]] | bool | None = None
    """Formatter options schema."""


@dataclass(frozen=True, kw_only=True)
class Formatter:
    """A formatter for linting results."""

    meta: FormatterMeta
    """The formatter metadata."""

    op_class: Type[FormatterOp]
    """The class that implements the format operation."""


class FormatterRegistry(Mapping[str, Formatter]):

    def __init__(self):
        self._registrations = {}

    def define_formatter(
        self,
        name: str | None = None,
        version: str | None = None,
        schema: dict[str, Any] | list[dict[str, Any]] | bool | None = None,
    ) -> Callable[[Any], Type[FormatterOp]]:

        def _define_formatter(op_class: Any) -> Type[FormatterOp]:
            from inspect import isclass

            if not isclass(op_class) or not issubclass(op_class, FormatterOp):
                raise TypeError(
                    f"component decorated by define_formatter()"
                    f" must be a subclass of {FormatterOp.__name__}"
                )
            meta = FormatterMeta(
                name=name or to_kebab_case(op_class.__name__),
                version=version,
                schema=schema,
            )
            self._registrations[meta.name] = Formatter(meta=meta, op_class=op_class)
            return op_class

        return _define_formatter

    def __getitem__(self, key: str) -> Formatter:
        return self._registrations[key]

    def __len__(self) -> int:
        return len(self._registrations)

    def __iter__(self):
        return iter(self._registrations)
