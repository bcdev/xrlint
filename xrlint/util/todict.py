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


def _convert_value(v: Any) -> Any:
    if hasattr(v, "to_dict") and callable(v.to_dict):
        return v.to_dict()
    elif isinstance(v, dict):
        return {k: _convert_value(v2) for k, v2 in v.items()}
    elif isinstance(v, (tuple, list)):
        return [_convert_value(v2) for v2 in v]
    return v
