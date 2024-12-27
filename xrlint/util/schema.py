from typing import Any, Literal

from .formatting import (
    format_message_type_of,
    format_message_one_of,
)

TYPE_NAMES = (
    "null",
    "boolean",
    "integer",
    "number",
    "string",
    "array",
    "object",
)

JsonTypeName = Literal[
    "null",
    "boolean",
    "integer",
    "number",
    "string",
    "array",
    "object",
]

JsonSchema = dict[str, Any] | bool


# noinspection PyPep8Naming
def schema(
    type: JsonTypeName | list[JsonTypeName] | None = None,
    *,
    # common
    default: Any | None = None,
    const: Any | None = None,
    enum: list[Any] | None = None,
    # "integer", "number"
    minimum: int | float | None = None,
    maximum: int | float | None = None,
    # "array"
    items: list[JsonSchema] | JsonSchema | None = None,
    # "object"
    properties: dict[str, JsonSchema] | None = None,
    additionalProperties: bool | None = None,
    required: list[str] | None = None,
) -> JsonSchema:
    return {
        k: v
        for k, v in dict(
            type=_parse_type(type),
            default=default,
            const=const,
            enum=enum,
            minimum=minimum,
            maximum=maximum,
            items=items,
            properties=properties,
            additionalProperties=False if additionalProperties is False else None,
            required=required,
        ).items()
        if v is not None
    }


def _parse_type(type: Any) -> JsonTypeName | list[JsonTypeName] | None:
    if isinstance(type, (list, tuple)):
        if not type:
            return None
        return [_validate_type_name(t) for t in type]
    else:
        if type is None:
            return None
        return _validate_type_name(type)


def _validate_type_name(type_name: Any) -> JsonTypeName:
    if not isinstance(type_name, str):
        raise TypeError(format_message_type_of("type", type_name, "str|list[str]"))
    if type_name not in TYPE_NAMES:
        raise ValueError(format_message_one_of("type name", type_name, TYPE_NAMES))
    # noinspection PyTypeChecker
    return type_name
