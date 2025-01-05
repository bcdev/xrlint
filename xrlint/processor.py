from abc import abstractmethod, ABC
from dataclasses import dataclass
from typing import Type, Any, Callable

import xarray as xr

from xrlint.result import Message


class ProcessorOp(ABC):
    """Implements the processor operations."""

    @abstractmethod
    def preprocess(
        self, file_path: str, opener_options: dict[str, Any]
    ) -> list[tuple[xr.Dataset, str]]:
        """Pre-process a dataset given by its `file_path` and `opener_options`.
        In this method you use the `file_path` to read zero, one, or more
        datasets to lint.

        Args:
            file_path: A file path
            opener_options: The configuration's `opener_options`.
        Returns:
            A list of (dataset, file_path) pairs
        """

    @abstractmethod
    def postprocess(
        self, messages: list[list[Message]], file_path: str
    ) -> list[Message]:
        """Post-process the outputs of each dataset from `preprocess()`.

        Args:
            messages: contains two-dimensional array of ´Message´ objects
                where each top-level array item contains array of lint messages
                related to the dataset that was returned in array from
                `preprocess()` method
            file_path: The corresponding file path

        Returns:
            A one-dimensional array (list) of the messages you want to keep
        """


@dataclass(frozen=True, kw_only=True)
class ProcessorMeta:
    """Processor metadata."""

    name: str
    """Name of the processor."""

    version: str = "0.0.0"
    """Version of the processor."""


@dataclass(frozen=True, kw_only=True)
class Processor:
    """Processors tell XRLint how to process files other than
    standard xarray datasets.
    """

    meta: ProcessorMeta
    """Information about the processor."""

    op_class: Type[ProcessorOp]
    """A class that implements the processor operations."""

    supports_auto_fix: bool = False
    """`True` if this processor supports auto-fixing of datasets."""


def register_processor(
    registry: dict[str, Processor],
    name: str,
    version: str = "0.0.0",
    op_class: Type[ProcessorOp] | None = None,
) -> Callable[[Any], Type[ProcessorOp]] | None:
    def _register_processor(_op_class: Any) -> Type[ProcessorOp]:
        from inspect import isclass

        if not isclass(_op_class) or not issubclass(_op_class, ProcessorOp):
            raise TypeError(
                f"component decorated by define_processor()"
                f" must be a subclass of {ProcessorOp.__name__}"
            )
        meta = ProcessorMeta(name=name, version=version)
        registry[name] = Processor(meta=meta, op_class=_op_class)
        return _op_class

    if op_class is None:
        # decorator case
        return _register_processor

    _register_processor(op_class)
