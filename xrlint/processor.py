from abc import abstractmethod, ABC
from dataclasses import dataclass
from typing import Type


import xarray as xr

from xrlint.result import Message


class ProcessorOp(ABC):
    """Implements the processor operations."""

    @abstractmethod
    def preprocess(
        self, dataset: xr.Dataset, file_path: str
    ) -> list[tuple[xr.Dataset, str]]:
        """Pre-process the dataset.
        In this method you can strip out any content
        and optionally split into multiple (or none)
        datasets to lint.

        Args:
            dataset: A dataset
            file_path: The file path that was used to open
                the `dataset`.
        Returns:
            An array of code blocks to lint
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
    name: str
    version: str


@dataclass(frozen=True, kw_only=True)
class Processor:
    meta: ProcessorMeta
    """Information about the processor."""

    op_class: Type[ProcessorOp]
    """A class that implements the processor operations."""

    supports_auto_fix: bool = False
    """`True` if this processor supports auto-fixing of datasets."""
