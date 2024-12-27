from dataclasses import dataclass
from typing import Any, Type
from abc import abstractmethod, ABC

from xrlint.result import Result


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
    name: str
    version: str
    schema: dict[str, Any] | list[dict[str, Any]] | bool | None = None


@dataclass(frozen=True, kw_only=True)
class Formatter:
    """A formatter for linting results."""

    meta: FormatterMeta
    """The formatter metadata."""

    op_class: Type[FormatterOp]
    """The class that implements the format operation."""
