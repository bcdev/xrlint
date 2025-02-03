#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from abc import ABC, abstractmethod
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any, Callable, Type

from xrlint.operation import Operation, OperationMeta
from xrlint.result import Result, ResultStats


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
class FormatterMeta(OperationMeta):
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
class Formatter(Operation):
    """A formatter for linting results."""

    meta: FormatterMeta
    """The formatter metadata."""

    op_class: Type[FormatterOp]
    """The class that implements the format operation."""

    @classmethod
    def meta_class(cls) -> Type:
        return FormatterMeta

    @classmethod
    def op_base_class(cls) -> Type:
        return FormatterOp

    @classmethod
    def value_name(cls) -> str:
        return "formatter"


class FormatterRegistry(Mapping[str, Formatter]):
    def __init__(self):
        self._registrations = {}

    def define_formatter(
        self,
        name: str | None = None,
        version: str | None = None,
        schema: dict[str, Any] | list[dict[str, Any]] | bool | None = None,
    ) -> Callable[[FormatterOp], Type[FormatterOp]] | Formatter:
        """Decorator function."""
        return Formatter.define_operation(
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
