from collections.abc import Mapping, Sequence
from functools import lru_cache
from inspect import formatannotation, signature, isclass, Signature, Parameter
from types import NoneType, UnionType
from typing import (
    Any,
    Generic,
    TypeVar,
    Type,
    TypeAlias,
    Union,
    get_origin,
    get_args,
    get_type_hints,
    Optional,
)

from xrlint.util.formatting import format_message_type_of


JSON_VALUE_TYPE_NAME = "None | bool | int | float | str | dict | list"

JsonValue: TypeAlias = (
    NoneType | bool | int | float | str | dict[str, "JsonValue"] | list["JsonValue"]
)

T = TypeVar("T")

_SIGNATURES: dict[type, Signature] = {}


class ValueConstructible(Generic[T]):
    """Can be used to make data classes constructible from a value.

    The factory for this purpose is the
    class method [from_value][xrlint.util.codec.ValueConstructible.from_value].
    """

    @classmethod
    def from_value(cls, value: Any, value_name: str | None = None) -> T:
        """Create an instance of this class from a value.

        Args:
            value: The value
            value_name: An identifier used for error messages.
                Defaults to the value returned by `cls._get_value_name()`.

        Returns:
            An instance of this class.

        Raises:
            TypeError: If `value` cannot be converted.
        """
        value_name = value_name or cls._get_value_name()
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
        if isinstance(value, type):
            if isclass(value) and issubclass(value, cls):
                return cls._from_class(value, value_name)
            else:
                return cls._from_type(value, value_name)
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
    def _from_class(cls, value: Type[T], value_name: str) -> T:
        """Create an instance of this class from a class value
        that is a subclass of `cls`.
        The default implementation raises a `TypeError`.
        Override to implement a different behaviour.
        """
        raise TypeError(cls._format_type_error(value, value_name))

    @classmethod
    def _from_type(cls, value: Type, value_name: str) -> T:
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
    def _convert_value(cls, value: Any, type_annotation: Any, value_name: str) -> Any:
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

        if type_origin is Union:
            # For unions try converting the alternatives.
            # Return the first successfully converted value.
            assert len(type_args) > 0
            errors = []
            for type_arg in type_args:
                try:
                    return cls._convert_value(value, type_arg, value_name)
                except (TypeError, ValueError) as e:
                    errors.append(e)
            # Note, this error message constructed here is suboptimal.
            # But we sometimes need all details to trace back to the
            # root cause while conversion failed.
            raise TypeError("\n".join(str(e) for e in errors))

        if issubclass(type_origin, ValueConstructible):
            # If origin is also a ValueConstructible, we are happy
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
                            format_message_type_of(f"keys of {value_name}", k, key_type)
                        )
                    mapping_value[k] = cls._convert_value(
                        v, item_type, f"{value_name}[{k!r}]"
                    )
                return mapping_value
            if issubclass(type_origin, Sequence):
                item_type = type_args[0] if type_args else Any
                # noinspection PyTypeChecker
                return [
                    cls._convert_value(v, item_type, f"{value_name}[{i}]")
                    for i, v in enumerate(value)
                ]
            return value

        raise TypeError(
            format_message_type_of(value_name, value, formatannotation(type_annotation))
        )

    @classmethod
    @lru_cache(maxsize=1000)
    def _get_class_parameters(cls) -> Mapping[str, Parameter]:
        """Get the type-resolved parameters of this class' constructor.
        The method returns a cached value for `cls`.

        Can be used by subclasses to process annotations.
        """
        forward_refs = cls._get_forward_refs()
        return get_class_parameters(cls, forward_refs=forward_refs)

    @classmethod
    def _get_forward_refs(cls) -> Optional[Mapping[str, type]]:
        """Get an extra namespace to be used for resolving parameter type hints.
        Called from [ValueConstructible._get_class_parameters][].

        Can be overridden to provide a namespace for resolving type
        forward references for your class.
        Defaults to `None`.
        """
        return None

    @classmethod
    def _get_value_name(cls) -> str:
        """Get an identifier for values that can be used to create
        instances of this class.

        Can be overridden to provide a custom, user-friendly value name.
        Defaults to `"value"`.
        """
        return "value"

    @classmethod
    def _get_value_type_name(cls) -> str:
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
        return type_origin, type_args

    @classmethod
    def _format_type_error(cls, value: Any, value_name: str) -> str:
        return format_message_type_of(value_name, value, cls._get_value_type_name())


class MappingConstructible(Generic[T], ValueConstructible[T]):
    """A `ValueConstructible` that accepts both instances of `T` and
    mappings (e.g., `dict`) as input values.
    """

    @classmethod
    def _from_mapping(cls, mapping: Mapping, value_name: str) -> T:
        """Create an instance of this class from a mapping value.

        The default implementation treats the mapping as keyword
        arguments passed to the class constructor.

        The use case for this is constructing instances of this class
        from JSON-objects.
        """

        mapping_keys = set(mapping.keys())
        properties = cls._get_class_parameters()

        args = []
        kwargs = {}
        for prop_name, prop_param in properties.items():
            if prop_name in mapping:
                mapping_keys.remove(prop_name)

                if prop_param.annotation is Parameter.empty:
                    prop_annotation = Any
                else:
                    prop_annotation = prop_param.annotation

                prop_value = cls._convert_value(
                    mapping[prop_name],
                    prop_annotation,
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
                    f" of type {cls._get_value_type_name()}"
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

    @classmethod
    def _get_value_type_name(cls) -> str:
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
            annotation = resolved_hints[name]
            resolved_params[name] = Parameter(
                name, param.kind, default=param.default, annotation=annotation
            )

    return resolved_params


class JsonSerializable:

    def to_json(self, name: str | None = None) -> JsonValue:
        return self.to_dict(name=name)

    def to_dict(self, name: str | None = None) -> dict[str, JsonValue]:
        return self._mapping_to_json(self.__dict__, name or type(self).__name__)

    @classmethod
    def _value_to_json(cls, value: Any, name: str) -> JsonValue:
        if value is None:
            # noinspection PyTypeChecker
            return None
        if isinstance(value, JsonSerializable):
            return value.to_json(name=name)
        if isinstance(value, bool):
            return bool(value)
        if isinstance(value, int):
            return int(value)
        if isinstance(value, float):
            return float(value)
        if isinstance(value, str):
            return str(value)
        if isinstance(value, Mapping):
            return cls._mapping_to_json(value, name)
        if isinstance(value, Sequence):
            return cls._sequence_to_json(value, name)
        if isinstance(value, type):
            return value.__name__
        raise TypeError(format_message_type_of(name, value, JSON_VALUE_TYPE_NAME))

    @classmethod
    def _mapping_to_json(cls, mapping: Mapping, name: str) -> dict[str, JsonValue]:
        return {
            k: cls._value_to_json(v, f"{name}.{k}")
            for k, v in mapping.items()
            if is_public_property_name(k)
        }

    @classmethod
    def _sequence_to_json(cls, sequence: Sequence, name: str) -> list[JsonValue]:
        return [cls._value_to_json(v, f"{name}[{i}]") for i, v in enumerate(sequence)]


def is_public_property_name(key: Any) -> bool:
    return (
        isinstance(key, str)
        and key.isidentifier()
        and not key[0].isupper()
        and not key[0] == "_"
    )