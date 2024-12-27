from typing import Any


def format_problems(error_count, warning_count):
    problem_count = error_count + warning_count
    p_label = format_count(problem_count, "problem")
    if problem_count == 0:
        return p_label
    e_label = format_count(error_count, "error")
    w_label = format_count(warning_count, "warning")
    if error_count and warning_count:
        return f"{p_label} ({e_label} and {w_label})"
    if error_count:
        return e_label
    else:
        return w_label


def format_count(count: int, name: str):
    """Format given `count` of items named by `name`."""
    if count == 0:
        return f"no {name}s"
    if count == 1:
        return f"one {name}"
    else:
        return f"{count} {name}s"


def format_message_one_of(name: str, value: Any, enum_value) -> str:
    if isinstance(enum_value, str):
        enum_text = enum_value
    else:
        enum_text = ", ".join(f"{v!r}" for v in enum_value)
    return f"{name} must be one of {enum_text}, but was {value!r}"


def format_message_type_of(name: str, value: Any, type_value: type | str) -> str:
    return (
        f"{name} must be of type {format_type_of(type_value)},"
        f" but was {format_type_of(type(value))}"
    )


def format_type_of(value: Any) -> str:
    if value is None or value is type(None):
        return "None"
    if isinstance(value, str):
        return value
    assert isinstance(value, type)
    return value.__name__
