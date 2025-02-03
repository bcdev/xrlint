#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Type

import xarray as xr

from xrlint.operation import Operation, OperationMeta
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


@dataclass(kw_only=True)
class ProcessorMeta(OperationMeta):
    """Processor metadata."""

    name: str
    """Processor name."""

    version: str = "0.0.0"
    """Processor version."""

    """Processor description. Optional."""
    description: str | None = None

    ref: str | None = None
    """Processor reference.
    Specifies the location from where the processor can be
    dynamically imported.
    Must have the form "<module>:<attr>", if given.
    """

    @classmethod
    def value_name(cls) -> str:
        return "processor_meta"

    @classmethod
    def value_type_name(cls) -> str:
        return "ProcessorMeta | dict"


@dataclass(frozen=True, kw_only=True)
class Processor(Operation):
    """Processors tell XRLint how to process files other than
    standard xarray datasets.
    """

    meta: ProcessorMeta
    """Information about the processor."""

    op_class: Type[ProcessorOp]
    """A class that implements the processor operations."""

    # Not yet:
    # supports_auto_fix: bool = False
    # """`True` if this processor supports auto-fixing of datasets."""

    @classmethod
    def meta_class(cls) -> Type:
        return ProcessorMeta

    @classmethod
    def op_base_class(cls) -> Type:
        return ProcessorOp

    @classmethod
    def value_name(cls) -> str:
        return "processor"


def define_processor(
    name: str | None = None,
    version: str = "0.0.0",
    registry: dict[str, Processor] | None = None,
    op_class: Type[ProcessorOp] | None = None,
) -> Callable[[Any], Type[ProcessorOp]] | Processor:
    """Define a processor.

    This function can be used to decorate your processor operation class
    definitions. When used as a decorator, the decorated operator class
    will receive a `meta` attribute of type
    [ProcessorMeta][xrlint.processor.ProcessorMeta].
    In addition, the `registry` if given, will be updated using `name`
    as key and a new [Processor][xrlint.processor.Processor] as value.

    Args:
        name: Processor name,
            see [ProcessorMeta][xrlint.processor.ProcessorMeta].
        version: Processor version,
            see [ProcessorMeta][xrlint.processor.ProcessorMeta].
        registry: Processor registry. Can be provided to register the
            defined processor using its `name`.
        op_class: Processor operation class. Must be `None`
            if this function is used as a class decorator.

    Returns:
        A decorator function, if `op_class` is `None` otherwise
            the value of `op_class`.

    Raises:
        TypeError: If either `op_class` or the decorated object is not a
            a class derived from [ProcessorOp][xrlint.processor.ProcessorOp].
    """
    return Processor.define_operation(
        op_class, registry=registry, meta_kwargs=dict(name=name, version=version)
    )
