from abc import abstractmethod, ABC
from dataclasses import dataclass
from typing import Type, Any

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

    Processors are note yet supported.
    """

    meta: ProcessorMeta
    """Information about the processor."""

    op_class: Type[ProcessorOp]
    """A class that implements the processor operations."""

    supports_auto_fix: bool = False
    """`True` if this processor supports auto-fixing of datasets."""
