from abc import ABC, abstractmethod
from collections.abc import MutableMapping
from dataclasses import dataclass
from inspect import isclass, getdoc
from typing import Any, Type, Callable

from xrlint.util.codec import (
    ValueConstructible,
    JsonSerializable,
    MappingConstructible,
    JsonValue,
)
from xrlint.util.importutil import import_value
from xrlint.util.naming import to_kebab_case


@dataclass(kw_only=True)
class OpMetadata(MappingConstructible["OpMetadata"], JsonSerializable):
    """Operation metadata."""

    name: str
    """Operation name."""

    version: str = "0.0.0"
    """Operation version."""

    """Operation description. Optional."""
    description: str | None = None

    ref: str | None = None
    """Operation reference.
    Specifies the location from where the operation can be
    dynamically imported.
    Must have the form "<module>:<attr>", if given.
    """

    def to_dict(self, value_name: str | None = None) -> dict[str, JsonValue]:
        return {
            k: v
            for k, v in super().to_dict(value_name=value_name).items()
            if v is not None
        }


class OpMixin(ValueConstructible["OpMixin"], JsonSerializable):
    """A mixin class that is used by operation classes.

    An operation class comprises a `meta` property
    that provides the operation metadata. See [OpMetadata][]
    for its interface definition.

    An `op_class` property holds a class that implements the
    operation's logic.

    Rules, processors, and formatters use this mixin.

    Derived classes should provide a constructor that takes at least
    two keyword arguments:

    - `meta` - the metadata object that describes the operation
    - `op_class` - the class that implements the operation

    The `meta` object's class is expected to be constructible
    from keyword arguments with at least a `name: str` argument.
    `meta` objects should also have a writable `ref: str | None`
    property.
    """

    # noinspection PyUnresolvedReferences
    def to_json(self, value_name: str | None = None) -> str:
        if self.meta.ref:
            return self.meta.ref
        return super().to_json(value_name=value_name)

    @classmethod
    def _from_class(cls, value: Type, value_name: str) -> "OpMixin":
        # noinspection PyTypeChecker
        if issubclass(value, cls.op_base_class):
            op_class = value
            try:
                # Note, the value.meta attribute is set by
                # the define_op
                #
                # noinspection PyUnresolvedReferences
                meta = op_class.meta
            except AttributeError:
                raise ValueError(
                    f"missing {cls.op_name} metadata, apply define_{cls.op_name}()"
                    f" to class {op_class.__name__}"
                )
            # noinspection PyArgumentList
            return cls(meta=meta, op_class=op_class)
        return super()._from_class(value, value_name)

    @classmethod
    def _from_str(cls, value: str, value_name: str) -> "OpMixin":
        # noinspection PyTypeChecker
        operator, operator_ref = import_value(
            value,
            cls.op_import_attr_name,
            factory=cls.from_value,
        )
        # noinspection PyUnresolvedReferences
        operator.meta.ref = operator_ref
        return operator

    @classmethod
    @property
    def op_import_attr_name(cls) -> str:
        """Get the default name for the attribute that is used to import
        instances of this class from modules.
        """
        return f"export_{cls.op_name}"

    @classmethod
    @property
    @abstractmethod
    def op_base_class(cls) -> Type:
        """Get the operation base class."""

    @classmethod
    @property
    @abstractmethod
    def op_name(cls) -> str:
        """Get a name that describes the operation, e.g.,
        "rule", "processor", "formatter".
        """
        return "operation"

    @classmethod
    def _get_value_name(cls) -> str:
        return cls.op_name

    @classmethod
    def _get_value_type_name(cls) -> str:
        return f"{cls.__name__} | Type[{cls.op_base_class.__name__}] | str"

    @classmethod
    def _define_op(
        cls,
        op_class: Type | None,
        meta_class: Type,
        *,
        registry: MutableMapping[str, "OpMixin"] | None = None,
        meta_kwargs: dict[str, Any] | None = None,
        **kwargs,
    ) -> Callable[[Type], Type] | "OpMixin":
        """Defines an operator.
        Implementation helper that is supposed to be used by
        subclasses in order to define operator and register
        them.
        """
        meta_kwargs = meta_kwargs or {}

        def _define_op(_op_class: Type, decorated=True) -> Type | "OpMixin":
            cls._assert_op_class_ok(f"decorated {cls.op_name} component", _op_class)

            name = meta_kwargs.pop("name", None)
            if not name:
                name = to_kebab_case(_op_class.__name__)
            description = meta_kwargs.pop("description", None)
            if not description:
                description = getdoc(_op_class)
            meta = meta_class(name=name, description=description, **meta_kwargs)

            # Register rule metadata in rule operation class
            _op_class.meta = meta

            # noinspection PyArgumentList
            op_instance = cls(meta=meta, op_class=_op_class, **kwargs)
            if registry is not None:
                # Register rule in rule registry
                registry[name] = op_instance
            if decorated:
                return _op_class
            else:
                return op_instance

        if registry is not None and not isinstance(registry, MutableMapping):
            raise TypeError(
                f"registry must be a MutableMapping, but got {type(registry).__name__}"
            )

        if not isclass(meta_class):
            raise TypeError(
                f"meta_class must be class, but got {type(meta_class).__name__}"
            )

        if op_class is not None:
            # passing op_class means, we should return operator instance
            cls._assert_op_class_ok("op_class", op_class)
            return _define_op(op_class, decorated=False)

        # used as decorator, return closure
        return _define_op

    @classmethod
    def _assert_op_class_ok(cls, value_name: str, op_class: Type):
        if not isclass(op_class):
            raise TypeError(
                f"{value_name} must be a class, but got {type(op_class).__name__}"
            )
        # noinspection PyTypeChecker
        if not issubclass(op_class, cls.op_base_class):
            raise TypeError(
                f"{value_name} must be a subclass of {cls.op_base_class.__name__},"
                f" but got {op_class.__name__}"
            )
