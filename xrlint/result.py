from dataclasses import dataclass, field
from typing import Literal, TYPE_CHECKING, Any
import html

from tabulate import tabulate

from xrlint.constants import SEVERITY_CODE_TO_NAME
from xrlint.constants import SEVERITY_ERROR
from xrlint.constants import SEVERITY_WARN
from xrlint.util.formatting import format_problems
from xrlint.util.formatting import format_message_type_of
from xrlint.util.todict import ToDictMixin

if TYPE_CHECKING:  # pragma: no cover
    from xrlint.config import Config
    from xrlint.rule import RuleMeta


@dataclass(frozen=True, kw_only=True)
class EditInfo(ToDictMixin):
    """Not used yet."""


@dataclass(frozen=True)
class Suggestion(ToDictMixin):
    desc: str
    """Description of the suggestion."""

    data: dict[str, None] | None = None
    """Data that can be referenced in the description."""

    fix: EditInfo | None = None
    """Not used yet."""

    @classmethod
    def from_value(cls, value: Any):
        if isinstance(value, Suggestion):
            return value
        if isinstance(value, str):
            return Suggestion(value)
        raise TypeError(format_message_type_of("value", value, "Suggestion|str"))


@dataclass(kw_only=True)
class Message(ToDictMixin):
    message: str
    """The error message."""

    node_path: str | None = None
    """Node path within the dataset.
    This property is None if the message does not 
    apply to a certain dataset node.
    """

    rule_id: str | None = None
    """The rule name that generated this lint message. 
    If this message is generated by the xrlint core 
    rather than rules, this is None.
    """

    severity: Literal[1, 2] | None = None
    """The severity of this message. 
    `1` means warning and `2` means error.
    """

    fatal: bool | None = None
    """True if this is a fatal error unrelated to a rule, 
    like a parsing error.
    """

    fix: EditInfo | None = None
    """The EditInfo object of autofix. 
    This property is None if this 
    message is not fixable.

    Not used yet.
    """

    suggestions: list[Suggestion] | None = None
    """The list of suggestions. Each suggestion is the pair 
    of a description and an EditInfo object to fix the dataset. 
    API users such as editor integrations can choose one of them 
    to fix the problem of this message. 
    This property is None if this message does not have any suggestions.
    """


@dataclass()
class Result(ToDictMixin):
    """The aggregated information of linting a dataset."""

    config: "Config"
    """Configuration."""

    file_path: str
    """The absolute path to the file of this result. 
    This is the string "<dataset>" if the file path is unknown 
    (when you didn't pass the `file_path` option to the 
    `xrlint.lint_dataset()` method).
    """

    messages: list[Message] = field(default_factory=list)
    """The array of message objects."""

    fixable_error_count: int = 0
    """The number of errors that can be fixed automatically by the fix constructor option."""

    fixable_warning_count: int = 0
    """The number of warnings that can be fixed automatically by the fix constructor option."""

    error_count: int = 0
    """The number of errors. This includes fixable errors and fatal errors."""

    fatal_error_count: int = 0
    """The number of fatal errors."""

    warning_count: int = 0
    """The number of warnings. This includes fixable warnings."""

    @classmethod
    def new(cls, config: "Config", file_path: str, messages: list[Message]):
        result = Result(config, file_path=file_path, messages=messages)
        for m in messages:
            result.warning_count += 1 if m.severity == SEVERITY_WARN else 0
            result.error_count += 1 if m.severity == SEVERITY_ERROR else 0
            result.fatal_error_count += 1 if m.fatal else 0
        return result

    def to_html(self) -> str:
        text = []
        escaped_path = html.escape(self.file_path)
        if not self.messages:
            text.append(f'<p role="file">{escaped_path} - ok</p>\n')
        else:
            text.append(f'<p role="file">{escaped_path}:</p>\n')
            table_data = []
            for m in self.messages:
                table_data.append(
                    [
                        m.node_path,
                        SEVERITY_CODE_TO_NAME.get(m.severity),
                        m.message,
                        m.rule_id,
                    ]
                )
            text.append(tabulate(table_data, headers=(), tablefmt="html"))
            text.append(
                '<p role="summary">'
                f"{format_problems(self.error_count, self.warning_count)}"
                "</p>\n"
            )
        return "".join(text)

    def _repr_html_(self) -> str:
        return self.to_html()


def get_rules_meta_for_results(results: list[Result]) -> dict[str, "RuleMeta"]:
    rules_meta = {}
    for result in results:
        for message in result.messages:
            if message.rule_id:
                rule = result.config.get_rule(message.rule_id)
                rules_meta[message.rule_id] = rule.meta
    return rules_meta
