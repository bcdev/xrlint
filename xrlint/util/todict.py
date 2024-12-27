from typing import Any


class ToDictMixin:
    def to_dict(self):
        return to_dict(self)


def to_dict(obj: Any) -> Any:
    return {
        k: _convert_value(v)
        for k, v in obj.__dict__.items()
        if v is not None and isinstance(k, str) and not k.startswith("_")
    }


def _convert_value(value: Any) -> Any:
    if hasattr(value, "to_dict") and callable(value.to_dict):
        return value.to_dict()
    elif isinstance(value, dict):
        return {k: _convert_value(v) for k, v in value.items()}
    elif isinstance(value, (tuple, list)):
        return [_convert_value(v) for v in value]
    return value
