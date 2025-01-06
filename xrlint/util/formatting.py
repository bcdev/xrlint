from typing import Any


def format_problems(error_count, warning_count) -> str:
    """Return human readable text for the given
    `error_count` and `warning_count`.
    """
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


def format_count(count: int, item_name: str, upper: bool | None = None) -> str:
    """Format given `count` of items named by `item_name`."""
    if count == 0:
        return f"{format_case('no', upper)} {item_name}s"
    if count == 1:
        return f"{format_case('one', upper)} {item_name}"
    else:
        return f"{count} {item_name}s"


def format_item(item_name: str, count: int, upper: bool | None = None) -> str:
    """Format given `item_name` given it occurs `count` times."""
    item_name = format_case(item_name, upper)
    return f"{item_name}s" if count != 1 else item_name


def format_case(text: str, upper: bool | None = None) -> str:
    """Return `text` with first character turned to uppercase or lowercase."""
    if not text or upper is None:
        return text
    return (text[0].upper() if upper else text[0].lower()) + text[1:]


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


def format_link(path_or_url: str, text: str | None = None):
    """Format the file path as a clickable link"""
    href = ("file://" + path_or_url) if "://" not in path_or_url else path_or_url
    return f"\033]8;;{href}\033\\{text or path_or_url}\033]8;;\033\\"


def format_severity(severity: int):
    """Format the text to appear as an error"""
    return format_error("error") if severity == 2 else format_warn("warn")


def format_rule(rule_name: str):
    """Format the text to appear as an error"""
    return f"\033[1;31m{text}\033[0m"


def format_error(text: str):
    """Format the text to appear as an error"""
    return f"\033[0;31m{text}\033[0m"


def format_warn(text: str):
    """Format the text to appear as a warning"""
    return f"\033[0;34m{text}\033[0m"


def format_styled(text: str, s: int | str = "", fg: int | str = "", bg: int | str = ""):
    """Format styled text"""
    style = ""
    if s != "":
        style += str(s)
    if fg != "":
        style += ";" + str(fg)
    if bg != "":
        style += (";" if style else ";;") + str(bg)
    return f"\033[{style}m{text}\033[0m"
