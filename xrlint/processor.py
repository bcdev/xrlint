from abc import abstractmethod, ABC
from dataclasses import dataclass
from inspect import isclass
from typing import Type, Any, Callable

import xarray as xr

from xrlint.result import Message
from xrlint.util.formatting import format_message_type_of
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


@dataclass(frozen=True, kw_only=True)
class ProcessorMeta:
    """Processor metadata."""

    name: str
    """Processor name."""

    version: str = "0.0.0"
    """Processor version."""

    ref: str | None = None
    """Processor module reference. 
    Specifies the location from where the processor can be loaded.
    Must have the form "<module>:<attr>".
    """

    @classmethod
    def from_value(cls, value: Any) -> "ProcessorMeta":
        if isinstance(value, ProcessorMeta):
            return value
        if isinstance(value, dict):
            return ProcessorMeta(
                name=value.get("name"),
                version=value.get("version"),
                ref=value.get("ref"),
            )
        raise TypeError(format_message_type_of("value", value, "ProcessorMeta|dict"))


@dataclass(frozen=True, kw_only=True)
class Processor:
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
    def from_value(cls, value: Any) -> "Processor":
        if isinstance(value, Processor):
            return value
        if isclass(value) and issubclass(value, ProcessorOp):
            # TODO: see code duplication in Rule.from_value()
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
        if isinstance(value, str):
            processor, processor_ref = import_value(
                value,
                "export_processor",
                factory=Processor.from_value,
                expected_type=type,
            )
            processor.meta.ref = processor_ref
            return processor
        if isinstance(value, dict):
            return Processor(
                meta=cls._parse_meta(value), op_class=cls._parse_op_class(value)
            )
        raise TypeError(
            format_message_type_of(
                "value", value, "str|dict|Processor|Type[ProcessorOp]"
            )
        )

    @classmethod
    def _parse_meta(cls, value: dict) -> "ProcessorMeta":
        meta = value.get("meta")
        if meta is None:
            raise ValueError("missing 'meta' property")
        return ProcessorMeta.from_value(meta)

    @classmethod
    def _parse_op_class(cls, value: dict) -> Type["ProcessorOp"]:
        op_class = value.get("op_class")
        if op_class is None:
            raise ValueError("missing 'op_class' property")
        if isclass(op_class) and issubclass(op_class, ProcessorOp):
            return op_class
        raise TypeError(
            format_message_type_of("op_class", op_class, "Type[ProcessorOp]")
        )


# TODO: see code duplication in define_rule()
def define_processor(
    name: str | None = None,
    version: str = "0.0.0",
    registry: dict[str, Processor] | None = None,
    op_class: Type[ProcessorOp] | None = None,
) -> Callable[[Any], Type[ProcessorOp]] | Processor:
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
            registry[name] = processor
        return processor if no_deco else _op_class

    if op_class is None:
        # decorator case
        return _define_processor
    else:
        return _define_processor(op_class, no_deco=True)
