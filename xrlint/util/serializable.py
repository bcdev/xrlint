#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from dataclasses import fields, is_dataclass
from typing import Any, Final, Mapping, Sequence, TypeAlias

from xrlint.util.formatting import format_message_type_of

JSON_VALUE_TYPE_NAME: Final = "None | bool | int | float | str | dict | list"

JsonValue: TypeAlias = (
    None | bool | int | float | str | dict[str, "JsonValue"] | list["JsonValue"]
)


class JsonSerializable:
    """A mixin that makes your classes serializable to JSON values
    and JSON-serializable dictionaries.

    It adds two methods:

    * [to_json][JsonSerializable.to_json] converts to JSON values
    * [to_dict][JsonSerializable.to_dict] converts to JSON-serializable
        dictionaries

    """

    def to_json(self, value_name: str | None = None) -> JsonValue:
        """Convert this object into a JSON value.

        The default implementation calls `self.to_dict()` and returns
        its value as-is.
        """
        return self.to_dict(value_name=value_name)

    def to_dict(self, value_name: str | None = None) -> dict[str, JsonValue]:
        """Convert this object into a JSON-serializable dictionary.

        The default implementation naively serializes the non-protected
        attributes of this object's dictionary given by `vars(self)`.
        """
        return self._object_to_json(self, value_name or type(self).__name__)

    @classmethod
    def _value_to_json(cls, value: Any, value_name: str) -> JsonValue:
        if value is None:
            return None
        if isinstance(value, JsonSerializable):
            return value.to_json(value_name=value_name)
        if isinstance(value, bool):
            return bool(value)
        if isinstance(value, int):
            return int(value)
        if isinstance(value, float):
            return float(value)
        if isinstance(value, str):
            return str(value)
        if isinstance(value, Mapping):
            return cls._mapping_to_json(value, value_name)
        if isinstance(value, Sequence):
            return cls._sequence_to_json(value, value_name)
        if isinstance(value, type):
            return repr(value)
        raise TypeError(format_message_type_of(value_name, value, JSON_VALUE_TYPE_NAME))

    @classmethod
    def _object_to_json(cls, value: Any, value_name: str) -> dict[str, JsonValue]:
        if is_dataclass(value):
            _d = {f.name: (f, getattr(value, f.name)) for f in fields(value)}
            d = {k: v for k, (f, v) in _d.items() if v != f.default}
        else:
            d = {
                k: v
                for k, v in vars(value).items()
                if cls._is_non_protected_property_name(k)
            }
        return {k: cls._value_to_json(v, f"{value_name}.{k}") for k, v in d.items()}

    @classmethod
    def _mapping_to_json(
        cls, mapping: Mapping, value_name: str
    ) -> dict[str, JsonValue]:
        return {
            str(k): cls._value_to_json(v, f"{value_name}[{k!r}]")
            for k, v in mapping.items()
        }

    @classmethod
    def _sequence_to_json(cls, sequence: Sequence, value_name: str) -> list[JsonValue]:
        return [
            cls._value_to_json(v, f"{value_name}[{i}]") for i, v in enumerate(sequence)
        ]

    @classmethod
    def _is_non_protected_property_name(cls, key: Any) -> bool:
        return (
            isinstance(key, str)
            and key.isidentifier()
            and not key[0].isupper()
            and not key[0] == "_"
        )
