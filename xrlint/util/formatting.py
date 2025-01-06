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


def format_styled(
    text: str = "", s: str = "", fg: str = "", bg: str = "", href: str = ""
):
    """Format styled text"""
    if not text:
        if not href:
            return ""
        text = href

    style = ""
    if s != "":
        style += _S_CODES.get(s, "")
    if fg != "":
        style += ";" + _FG_CODES.get(fg, "")
    if bg != "":
        style += (";" if style else ";;") + _BG_CODES.get(bg, "")

    if style:
        styled_text = f"\033[{style}m{text}\033[0m"
    else:
        styled_text = text

    if not href:
        return styled_text
    if "://" in href:
        url = href
    else:
        url = "file://" + href
    return f"\033]8;;{url}\033\\{styled_text}\033]8;;\033\\"


_S_CODES = {
    k: str(c)
    for k, c in (
        ("normal", 0),
        ("bold", 1),
        ("dim", 2),
        ("italic", 3),
        ("underline", 4),
        ("blink", 5),
        ("reverse", 7),
    )
}

_C_CODES = (
    ("black", 30, 40),
    ("red", 31, 41),
    ("green", 32, 42),
    ("yellow", 33, 43),
    ("blue", 34, 44),
    ("magenta", 35, 45),
    ("cyan", 36, 46),
    ("white", 37, 47),
)

_FG_CODES = {k: str(c) for k, c, _ in _C_CODES}
_BG_CODES = {k: str(c) for k, _, c in _C_CODES}
