#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

import sys
from collections.abc import Mapping, Sequence
from functools import lru_cache
from inspect import Parameter, formatannotation, isclass, signature
from types import NoneType, UnionType
from typing import (
    Any,
    Generic,
    Literal,
    Optional,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

from xrlint.util.formatting import format_message_one_of, format_message_type_of

T = TypeVar("T")

_IS_PYTHON_3_10 = (3, 10) <= sys.version_info < (3, 11)


class ValueConstructible(Generic[T]):
    """A mixin that makes your classes constructible from a single value
    of any type.

    Implementing classes override one of the many `_from_<type>()`
    class methods to implement support converting from values of
    type `<type>`. They may use the [_from_typed_value][] to convert values
    from values with given type annotations, such as object properties
    or constructor parameters.

    The factory for this purpose is the
    class method [from_value][xrlint.util.codec.ValueConstructible.from_value].
    """

    @classmethod
    def from_value(cls, value: Any, value_name: str | None = None) -> T:
        """Create an instance of this class from a value.

        The default implementation checks if `value` is already an
        instance of this class. If so, it is returned unchanged.

        It then delegates to various `_from_<type>()` methods which
        all raise `TypeError` by default.

        Args:
            value: The value
            value_name: An identifier used for error messages.
                Defaults to the value returned by `cls._get_value_name()`.

        Returns:
            An instance of this class.

        Raises:
            TypeError: If `value` cannot be converted.
        """
        value_name = value_name or cls.value_name()
        if isinstance(value, cls):
            return value
        if value is None:
            return cls._from_none(value_name)
        if isinstance(value, bool):
            return cls._from_bool(value, value_name)
        if isinstance(value, int):
            return cls._from_int(value, value_name)
        if isinstance(value, float):
            return cls._from_float(value, value_name)
        if isinstance(value, str):
            return cls._from_str(value, value_name)
        if isinstance(value, Mapping):
            return cls._from_mapping(value, value_name)
        if isinstance(value, Sequence):
            return cls._from_sequence(value, value_name)
        if isclass(value):
            return cls._from_class(value, value_name)
        return cls._from_other(value, value_name)

    @classmethod
    def _from_none(cls, value_name: str) -> T:
        """Create an instance of this class from a `None` value.
        The default implementation raises a `TypeError`.
        Override to implement a different behaviour.
        """
        raise TypeError(cls._format_type_error(None, value_name))

    @classmethod
    def _from_bool(cls, value: bool, value_name: str) -> T:
        """Create an instance of this class from a bool value.
        The default implementation raises a `TypeError`.
        Override to implement a different behaviour.
        """
        raise TypeError(cls._format_type_error(value, value_name))

    @classmethod
    def _from_int(cls, value: int, value_name: str) -> T:
        """Create an instance of this class from an int value.
        The default implementation raises a `TypeError`.
        Override to implement a different behaviour.
        """
        raise TypeError(cls._format_type_error(value, value_name))

    @classmethod
    def _from_float(cls, value: float, value_name: str) -> T:
        """Create an instance of this class from a float value.
        The default implementation raises a `TypeError`.
        Override to implement a different behaviour.
        """
        raise TypeError(cls._format_type_error(value, value_name))

    @classmethod
    def _from_str(cls, value: str, value_name: str) -> T:
        """Create an instance of this class from a str value.
        The default implementation raises a `TypeError`.
        Override to implement a different behaviour.
        """
        raise TypeError(cls._format_type_error(value, value_name))

    @classmethod
    def _from_class(cls, value: Type, value_name: str) -> T:
        """Create an instance of this class from a type value.
        The default implementation raises a `TypeError`.
        Override to implement a different behaviour.
        """
        raise TypeError(cls._format_type_error(value, value_name))

    @classmethod
    def _from_other(cls, value: Any, value_name: str) -> T:
        """Create an instance of this class from a value of
        an unknown type.
        The default implementation raises a `TypeError`.
        Override to implement a different behaviour.
        """
        raise TypeError(cls._format_type_error(value, value_name))

    @classmethod
    def _from_mapping(cls, value: Mapping, value_name: str) -> T:
        """Create an instance of this class from a mapping value.
        The default implementation raises a `TypeError`.
        Override to implement a different behaviour.
        """
        raise TypeError(cls._format_type_error(value, value_name))

    @classmethod
    def _from_sequence(cls, value: Sequence, value_name: str) -> T:
        """Create an instance of this class from a sequence value.
        The default implementation raises a `TypeError`.
        Override to implement a different behaviour.
        """
        raise TypeError(cls._format_type_error(value, value_name))

    @classmethod
    def _convert_typed_value(
        cls, value: Any, type_annotation: Any, value_name: str
    ) -> Any:
        """To be used by subclasses that wish to convert a value with
        known type for the target value.

        Args:
            value: The value to convert to an instance of the
               type specified by `type_annotation`.
            type_annotation: The annotation representing the target type.
            value_name: An identifier for `value`.

        Returns:
            The converted value.
        """
        type_origin, type_args = cls._process_annotation(type_annotation)

        if value is None:
            # If value is None, ensure value is nullable.
            nullable = (
                type_origin is Any
                or type_origin is NoneType
                or type_origin is Union
                and (Any in type_args or NoneType in type_args)
            )
            if not nullable:
                raise TypeError(cls._format_type_error(value, value_name))
            return None

        if type_origin is Any:
            # We cannot do any further type checking,
            # therefore return the value as-is
            return value

        if type_origin is Literal:
            # Value must be one of literal arguments
            if value not in type_args:
                raise TypeError(format_message_one_of(value_name, value, type_args))
            return value

        if type_origin is Union:
            # For unions try converting the alternatives.
            # Return the first successfully converted value.
            assert len(type_args) > 0
            errors = []
            for type_arg in type_args:
                try:
                    return cls._convert_typed_value(value, type_arg, value_name)
                except (TypeError, ValueError) as e:
                    errors.append((type_arg, e))
            # Note, the error message constructed here is suboptimal.
            # But we sometimes need all details to trace back to the
            # root cause while conversion failed.
            raise TypeError(
                "all type alternatives failed:\n"
                + "\n".join(f"  {formatannotation(a)} --> {e}" for a, e in errors)
            )

        # if origin is a real type and value is of type origin
        if isclass(type_origin):
            # If origin is also a ValueConstructible, we are happy
            if issubclass(type_origin, ValueConstructible):
                return type_origin.from_value(value, value_name=value_name)

            if isinstance(value, type_origin):
                # If value has a compatible type, check first if we
                # can take care of special types, i.e., mappings and sequences.
                if isinstance(value, (bool, int, float, str)):
                    # We take a shortcut here. However, str test
                    # is important, because str is also a sequence!
                    return value

                if issubclass(type_origin, Mapping):
                    key_type, item_type = type_args if type_args else (Any, Any)
                    mapping_value = {}
                    # noinspection PyUnresolvedReferences
                    for k, v in value.items():
                        if not isinstance(k, key_type):
                            raise TypeError(
                                format_message_type_of(
                                    f"keys of {value_name}", k, key_type
                                )
                            )
                        mapping_value[k] = cls._convert_typed_value(
                            v, item_type, f"{value_name}[{k!r}]"
                        )
                    return mapping_value

                if issubclass(type_origin, Sequence):
                    item_type = type_args[0] if type_args else Any
                    # noinspection PyTypeChecker
                    return [
                        cls._convert_typed_value(v, item_type, f"{value_name}[{i}]")
                        for i, v in enumerate(value)
                    ]
                return value

        raise TypeError(
            format_message_type_of(value_name, value, formatannotation(type_annotation))
        )

    @classmethod
    @lru_cache(maxsize=1000)
    def class_parameters(cls) -> Mapping[str, Parameter]:
        """Get the type-resolved parameters of this class' constructor.
        The method returns a cached value for `cls`.

        Can be used by subclasses to process annotations.
        """
        return get_class_parameters(cls, forward_refs=cls.forward_refs())

    @classmethod
    def forward_refs(cls) -> Optional[Mapping[str, type]]:
        """Get an extra namespace to be used for resolving parameter type hints.
        Called from [ValueConstructible._get_class_parameters][].

        Can be overridden to provide a namespace for resolving type
        forward references for your class.
        Defaults to `None`.
        """
        return None

    @classmethod
    def value_name(cls) -> str:
        """Get an identifier for values that can be used to create
        instances of this class.

        Can be overridden to provide a custom, user-friendly value name.
        Defaults to `"value"`.
        """
        return "value"

    @classmethod
    def value_type_name(cls) -> str:
        """Get a descriptive name for the value types that can
        be used to create instances of this class, e.g., `"Rule | str"`.

        Can be overridden to provide a custom, user-friendly type name.
        Defaults to this class' name.
        """
        return cls.__name__

    @classmethod
    def _process_annotation(
        cls, prop_annotation: Any
    ) -> tuple[type | UnionType, tuple[type | UnionType, ...]]:
        type_origin = get_origin(prop_annotation)
        if type_origin is not None:
            type_origin = Union if type_origin is UnionType else type_origin
            type_args = get_args(prop_annotation)
        else:
            type_origin = prop_annotation
            type_args = ()
        if _IS_PYTHON_3_10:  # pragma: no cover
            forward_refs = cls.forward_refs()
            type_origin = cls._resolve_forward_ref(forward_refs, type_origin)
            type_args = tuple(
                cls._resolve_forward_ref(forward_refs, type_arg)
                for type_arg in type_args
            )
        return type_origin, type_args

    @classmethod
    def _resolve_forward_ref(cls, namespace, ref: Any) -> Any:  # pragma: no cover
        if isinstance(ref, str) and namespace:
            return namespace.get(ref, ref)
        else:
            return ref

    @classmethod
    def _format_type_error(cls, value: Any, value_name: str) -> str:
        return format_message_type_of(value_name, value, cls.value_type_name())


class MappingConstructible(Generic[T], ValueConstructible[T]):
    """A mixin that makes your classes constructible from mappings,
    such as a `dict`.

    The default implementation checks if `value` is already an
    instance of this class. If so, it is returned unchanged.

    It then delegates to various `_from_<type>()` methods which
    all raise `TypeError` by default, except for `_from_mapping()`.
    The latter is overridden to deserialize the items of the given
    mapping into values that will be passed to match constructor
    parameters. Type annotations of the parameters will be used
    to perform a type-safe conversion of the mapping values.

    The major use case for this is constructing instances of this
    class from JSON objects.
    """

    @classmethod
    def _from_mapping(cls, mapping: Mapping, value_name: str) -> T:
        """Create an instance of this class from a mapping value."""

        mapping_keys = set(mapping.keys())
        properties = cls.class_parameters()

        args = []
        kwargs = {}
        for prop_name, prop_param in properties.items():
            if prop_name in mapping:
                mapping_keys.remove(prop_name)

                if prop_param.annotation is Parameter.empty:
                    prop_annotation = Any
                else:
                    prop_annotation = prop_param.annotation

                prop_value = cls._convert_property_value(
                    mapping[prop_name],
                    prop_annotation,
                    prop_name,
                    value_name=f"{value_name}.{prop_name}",
                )
                if prop_param.kind == Parameter.POSITIONAL_ONLY:
                    args.append(prop_value)
                else:
                    kwargs[prop_name] = prop_value
            elif (
                prop_param.default is Parameter.empty
            ) or prop_param.kind == Parameter.POSITIONAL_ONLY:
                raise TypeError(
                    f"missing value for required property {value_name}.{prop_name}"
                    f" of type {cls.value_type_name()}"
                )

        if mapping_keys:
            invalid_keys = tuple(
                filter(lambda k: not isinstance(k, str), mapping.keys())
            )
            if invalid_keys:
                invalid_type = type(invalid_keys[0])
                raise TypeError(
                    f"mappings used to instantiate {value_name}"
                    f" of type {cls.__name__}"
                    f" must have keys of type str,"
                    f" but found key of type {invalid_type.__name__}"
                )

            raise TypeError(
                f"{', '.join(sorted(mapping_keys))}"
                f" {'is not a member' if len(mapping_keys) == 1 else 'are not members'}"
                f" of {value_name} of type {cls.__name__}"
            )

        # noinspection PyArgumentList
        return cls(*args, **kwargs)

    # noinspection PyUnusedLocal
    @classmethod
    def _convert_property_value(
        cls, value: Any, prop_annotation: Any, prop_name: str, value_name: str
    ) -> Any:
        """Convert a property value to the given type.

        May be overridden by subclasses that wish to perform a special
        conversion for a specific property.

        Args:
            value: The mapping's item value to convert to an instance of the
                type specified by `prop_annotation`.
            prop_annotation: The property annotation representing the
                target type.
            prop_name: The property name. May be used by overrides.
            value_name: An identifier for `value`.

        Returns:
            The converted property value.
        """
        return cls._convert_typed_value(
            value,
            prop_annotation,
            value_name=value_name,
        )

    @classmethod
    def value_type_name(cls) -> str:
        """Get a descriptive name for the value types that can
        be used to create instances of this class, e.g., `"Rule | str"`.
        Defaults to `f"{cls.__name__} | dict[str, Any]"`.
        """
        return f"{cls.__name__} | dict[str, Any]"


def get_class_parameters(
    cls, forward_refs: Mapping[str, type] | None = None
) -> Mapping[str, Parameter]:
    """Get the type-resolved parameters of this class' constructor.
    The returned value is cached.

    Args:
        cls: The class to inspect.
        forward_refs: Optional extra namespace from which to
            resolve forward references.

    Returns:
        A mapping from parameter names to parameters.
    """
    # Get the signature of the constructor
    sig = signature(cls.__init__)

    # Resolve annotations
    resolved_hints = get_type_hints(cls.__init__, localns=forward_refs)

    # Process the parameters
    resolved_params = {}
    for i, (name, param) in enumerate(sig.parameters.items()):
        if i > 0:  # Skip `self`
            annotation = resolved_hints.get(name, Parameter.empty)
            resolved_params[name] = Parameter(
                name, param.kind, default=param.default, annotation=annotation
            )

    return resolved_params
