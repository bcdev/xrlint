from collections.abc import Mapping, Sequence
from inspect import getfullargspec, isclass
from types import NoneType, UnionType
from typing import Any, Generic, TypeVar, Type, TypeAlias, Union, get_origin, get_args

from xrlint.util.formatting import format_message_type_of


JSON_TYPE_SPEC = "None|bool|int|float|str|dict|list|tuple"

JsonValue: TypeAlias = (
    NoneType | bool | int | float | str | dict[str, "JsonValue"] | list["JsonValue"]
)

T = TypeVar("T")

_PROPERTIES: dict[type, dict[str, Any]] = {}


class ValueConstructible(Generic[T]):

    @classmethod
    def from_value(cls, value: Any, name: str | None = None) -> T:
        """Decode value of any type into T."""
        name = name or cls._get_value_name()
        if isinstance(value, cls):
            return value
        if value is None:
            return cls._from_null(name)
        if isinstance(value, bool):
            return cls._from_bool(value, name)
        if isinstance(value, int):
            return cls._from_int(value, name)
        if isinstance(value, float):
            return cls._from_float(value, name)
        if isinstance(value, str):
            return cls._from_str(value, name)
        if isinstance(value, Mapping):
            return cls._from_mapping(value, name)
        if isinstance(value, Sequence):
            return cls._from_sequence(value, name)
        if isclass(value):
            return cls._from_class(value, name)
        return cls._from_other(value, name)

    @classmethod
    def _from_null(cls, name: str) -> T:
        raise TypeError(cls._format_type_error(name, None))

    @classmethod
    def _from_bool(cls, value: bool, name: str) -> T:
        raise TypeError(cls._format_type_error(name, value))

    @classmethod
    def _from_int(cls, value: int, name: str) -> T:
        raise TypeError(cls._format_type_error(name, value))

    @classmethod
    def _from_float(cls, value: float, name: str) -> T:
        raise TypeError(cls._format_type_error(name, value))

    @classmethod
    def _from_str(cls, value: str, name: str) -> T:
        raise TypeError(cls._format_type_error(name, value))

    @classmethod
    def _from_class(cls, value: Type, name: str) -> T:
        raise TypeError(cls._format_type_error(name, value))

    @classmethod
    def _from_mapping(cls, mapping: Mapping, name: str) -> T:
        for k in mapping.keys():
            if not isinstance(k, str):
                raise TypeError(
                    f"{name} of type {type(mapping).__name__}"
                    f" must have keys of type str, but key type was {type(k).__name__}"
                )
        properties = cls._get_properties()
        unexpected = set(mapping.keys()).difference(properties.keys())
        if unexpected:
            raise TypeError(
                f"{', '.join(sorted(unexpected))}"
                f" {'is not a member' if len(unexpected) == 1 else 'are not members'}"
                f" of {name} of type {cls.__name__}"
            )
        kwargs = {
            prop_name: cls.from_property(
                prop_name,
                mapping[prop_name],
                prop_annotation,
                name=f"{name}.{prop_name}",
            )
            for prop_name, prop_annotation in properties.items()
            if prop_name in mapping
        }
        # noinspection PyArgumentList
        return cls(**kwargs)

    @classmethod
    def from_property(
        cls, prop_name: str, prop_value: Any, prop_annotation: Any, name: str
    ):
        type_origin = get_origin(prop_annotation)
        if type_origin is not None:
            type_origin = Union if type_origin is UnionType else type_origin
            type_args = get_args(prop_annotation)
        else:
            type_origin = prop_annotation
            type_args = ()

        if prop_value is None:
            if (
                type_origin is Any
                or type_origin is NoneType
                or type_origin is Union
                and (Any in type_args or NoneType in type_args)
            ):
                return None
            raise TypeError(cls._format_type_error(name, prop_value))

        if type_origin is Union:
            assert len(type_args) > 0
            first_e = None
            for type_arg in type_args:
                try:
                    return cls.from_property(prop_name, prop_value, type_arg, name)
                except TypeError as e:
                    first_e = e if first_e is None else first_e
            raise first_e

        if issubclass(type_origin, ValueConstructible):
            return type_origin.from_value(prop_value, name=name)

        if type_origin is Any:
            return prop_value

        if isinstance(prop_value, type_origin):
            if isinstance(prop_value, (bool, int, float, str)):
                return prop_value
            if issubclass(type_origin, Mapping):
                key_type, item_type = type_args if type_args else (Any, Any)
                mapping_value = {}
                # noinspection PyUnresolvedReferences
                for k, v in prop_value.items():
                    if not isinstance(k, key_type):
                        raise TypeError("Aaaaaaaaaaaaargh!")
                    mapping_value[k] = cls.from_property(
                        prop_name, v, item_type, name=f"{name}.{k}"
                    )
                return mapping_value
            if issubclass(type_origin, Sequence):
                item_type = type_args[0] if type_args else Any
                # noinspection PyTypeChecker
                return [
                    cls.from_property(prop_name, v, item_type, name=f"{name}.{i}")
                    for i, v in enumerate(prop_value)
                ]
            return prop_value

        raise TypeError("invalid type")  # TODO: format message

    @classmethod
    def _from_sequence(cls, value: Sequence, name: str) -> T:
        raise TypeError(cls._format_type_error(name, value))

    @classmethod
    def _from_other(cls, value: Any, name: str) -> T:
        raise TypeError(cls._format_type_error(name, value))

    @classmethod
    def _format_type_error(cls, name: str, value: Any) -> str:
        return format_message_type_of(name, value, cls._get_type_name())

    @classmethod
    def _get_properties(cls) -> dict[str, Any]:
        properties = _PROPERTIES.get(cls)
        if properties is None:
            properties = {
                k: v
                for k, v in getfullargspec(cls).annotations.items()
                if k != "return"
            }
            _PROPERTIES[cls] = properties
        return properties

    @classmethod
    def _get_value_name(cls) -> str:
        return "value"

    @classmethod
    def _get_type_name(cls) -> str:
        return cls.__name__


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
        raise TypeError(format_message_type_of(name, value, JSON_TYPE_SPEC))

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
