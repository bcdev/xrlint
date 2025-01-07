from collections.abc import Sequence

from typing import Any


def format_problems(error_count: int, warning_count: int) -> str:
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


def format_count(
    count: int,
    singular: str,
    plural: str | None = None,
    upper: bool | None = None,
) -> str:
    """Format given `count` of items named by `singular` or `plural`."""
    if count == 0:
        count_text = format_case("no", upper)
    elif count == 1:
        count_text = format_case("one", upper)
    else:
        count_text = str(count)
    return f"{count_text} {format_item(count, singular, plural=plural)}"


def format_item(
    count: int, singular: str, plural: str | None = None, upper: bool | None = None
) -> str:
    """Format `singular` given it occurs `count` times."""
    if count == 1:
        name_text = singular
    else:
        name_text = plural or (singular + "s")
    return format_case(name_text, upper)


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


def format_seq(seq: Sequence, max_count: int = 6) -> str:
    if len(seq) == 0:
        return ""
    elif len(seq) <= max_count:
        return _format_seq(seq)
    else:
        i = max_count // 2
        return f"{_format_seq(seq[:i])}, ..., {_format_seq(seq[-i:])}"


def _format_seq(seq: Sequence) -> str:
    return ", ".join(str(v) for v in seq)


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
