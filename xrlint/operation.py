#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from collections.abc import MutableMapping
from dataclasses import dataclass
from inspect import getdoc, isclass
from typing import Any, Callable, Type

from xrlint.util.constructible import MappingConstructible
from xrlint.util.importutil import import_value
from xrlint.util.naming import to_kebab_case
from xrlint.util.serializable import JsonSerializable, JsonValue


@dataclass(kw_only=True)
class OperationMeta(MappingConstructible["OpMetadata"], JsonSerializable):
    """Operation metadata."""

    name: str
    """Operation name."""

    version: str = "0.0.0"
    """Operation version."""

    """Operation description. Optional."""
    description: str | None = None

    schema: dict[str, JsonValue] | list[dict[str, JsonValue]] | None = None
    """JSON Schema used to specify and validate the operation's'
    options, if any.

    It can take the following values:

    - Use `None` (the default) to indicate that the operation
      as no options at all.
    - Use a schema to indicate that the operation
      takes keyword arguments only.
      The schema's JSON type must be `"object"`.
    - Use a list of schemas to indicate that the operation
      takes positional-only arguments.
      If given, the number of schemas in the list specifies the
      number of positional arguments that must be provided by users.
    """

    ref: str | None = None
    """Operation reference.
    Specifies the location from where the operation can be
    dynamically imported.
    Must have the form "<module>:<attr>", if given.
    """


class Operation(MappingConstructible["Operation"], JsonSerializable):
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
    def _from_class(cls, value: Type, value_name: str) -> "Operation":
        # noinspection PyTypeChecker
        if issubclass(value, cls.op_base_class()):
            op_class = value
            try:
                # Note, the value.meta attribute is set by
                # the define_op
                #
                # noinspection PyUnresolvedReferences
                meta = op_class.meta
            except AttributeError:
                raise ValueError(
                    f"missing {cls.value_name()} metadata, apply define_{cls.value_name()}()"
                    f" to class {op_class.__name__}"
                )
            # noinspection PyArgumentList
            return cls(meta=meta, op_class=op_class)
        return super()._from_class(value, value_name)

    @classmethod
    def _from_str(cls, value: str, value_name: str) -> "Operation":
        # noinspection PyTypeChecker
        operator, operator_ref = import_value(
            value,
            cls.op_import_attr_name(),
            factory=cls.from_value,
        )
        # noinspection PyUnresolvedReferences
        operator.meta.ref = operator_ref
        return operator

    @classmethod
    def op_import_attr_name(cls) -> str:
        """Get the default name for the attribute that is used to import
        instances of this class from modules.
        """
        return f"export_{cls.value_name()}"

    @classmethod
    def meta_class(cls) -> Type:
        """Get the class of the instances of the `meta` field.
        Defaults to [OperationMeta][xrlint.operation.OperationMeta].
        """
        return OperationMeta

    @classmethod
    def op_base_class(cls) -> Type:
        """Get the base class from which all instances of the `op_class`
        must derive from.
        """
        return type

    @classmethod
    def value_name(cls) -> str:
        """Get a name that describes the operation, e.g.,
        "rule", "processor", "formatter".
        """
        return "operation"

    @classmethod
    def value_type_name(cls) -> str:
        return f"{cls.__name__} | Type[{cls.op_base_class().__name__}] | dict | str"

    @classmethod
    def define_operation(
        cls,
        op_class: Type | None,
        *,
        registry: MutableMapping[str, "Operation"] | None = None,
        meta_kwargs: dict[str, Any] | None = None,
        **kwargs,
    ) -> Callable[[Type], Type] | "Operation":
        """Defines an operation."""
        meta_kwargs = meta_kwargs or {}

        def _define_op(_op_class: Type, decorated=True) -> Type | "Operation":
            cls._assert_op_class_ok(
                f"decorated {cls.value_name()} component", _op_class
            )

            name = meta_kwargs.pop("name", None)
            if not name:
                name = to_kebab_case(_op_class.__name__)
            description = meta_kwargs.pop("description", None)
            if not description:
                description = getdoc(_op_class)
            schema = meta_kwargs.pop("schema", None)
            if schema is None:
                # TODO: if schema not given,
                #   derive it from _op_class' ctor arguments
                # schema = cls._derive_schema(_op_class)
                pass
            # noinspection PyCallingNonCallable
            meta = cls.meta_class()(
                name=name, description=description, schema=schema, **meta_kwargs
            )

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

        if op_class is not None:
            # passing the op_class means an operation instance is expected
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
        if not issubclass(op_class, cls.op_base_class()):
            raise TypeError(
                f"{value_name} must be a subclass of {cls.op_base_class().__name__},"
                f" but got {op_class.__name__}"
            )
