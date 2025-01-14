from abc import abstractmethod, ABC
from dataclasses import dataclass
from inspect import isclass
from typing import Type, Any, Callable

import xarray as xr

from xrlint.result import Message
from xrlint.util.codec import MappingConstructible
from xrlint.util.importutil import import_value
from xrlint.util.naming import to_kebab_case


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
class ProcessorMeta(MappingConstructible):
    """Processor metadata."""

    name: str
    """Processor name."""

    version: str = "0.0.0"
    """Processor version."""

    ref: str | None = None
    """Processor reference.
    Specifies the location from where the processor can be
    dynamically imported.
    Must have the form "<module>:<attr>", if given.
    """

    @classmethod
    def _get_value_type_name(cls) -> str:
        return "ProcessorMeta | dict"


@dataclass(frozen=True, kw_only=True)
class Processor(MappingConstructible):
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
    def _from_type(cls, value: Type[ProcessorOp], value_name: str) -> "Processor":
        # TODO: no test covers Processor._from_type
        if issubclass(value, ProcessorOp):
            # TODO: fix code duplication in Rule._from_class()
            try:
                # Note, the value.meta attribute is set by
                # the define_rule
                # noinspection PyUnresolvedReferences
                return Processor(meta=value.meta, op_class=value)
            except AttributeError:
                raise ValueError(
                    f"missing processor metadata, apply define_processor()"
                    f" to class {value.__name__}"
                )
        return super()._from_type(value, value_name)

    @classmethod
    def _from_str(cls, value: str, value_name: str) -> "Processor":
        processor, processor_ref = import_value(
            value,
            "export_processor",
            factory=Processor.from_value,
        )
        # noinspection PyUnresolvedReferences
        processor.meta.ref = processor_ref
        return processor

    @classmethod
    def _get_value_type_name(cls) -> str:
        return "str | dict | Processor | Type[ProcessorOp]"


# TODO: fix this code duplication in define_rule()
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
        op_class: Processor operation class. Must not be provided
            if this function is used as a class decorator.

    Returns:
        A decorator function, if `op_class` is `None` otherwise
            the value of `op_class`.

    Raises:
        TypeError: If either `op_class` or the decorated object is not a
            a class derived from [ProcessorOp][xrlint.processor.ProcessorOp].
    """

    def _define_processor(
        _op_class: Any, no_deco=False
    ) -> Type[ProcessorOp] | Processor:
        if not isclass(_op_class) or not issubclass(_op_class, ProcessorOp):
            raise TypeError(
                f"component decorated by define_processor()"
                f" must be a subclass of {ProcessorOp.__name__}"
            )
        meta = ProcessorMeta(
            name=name or to_kebab_case(_op_class.__name__),
            version=version,
        )
        setattr(_op_class, "meta", meta)
        processor = Processor(meta=meta, op_class=_op_class)
        if registry is not None:
            registry[meta.name] = processor
        return processor if no_deco else _op_class

    if op_class is None:
        # decorator case
        return _define_processor
    else:
        return _define_processor(op_class, no_deco=True)
