from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal, Union

from xrlint.constants import (
    CORE_PLUGIN_NAME,
    CORE_DOCS_URL,
    MISSING_DATASET_FILE_PATH,
    SEVERITY_ERROR,
    SEVERITY_WARN,
)
from xrlint.util.constructible import ValueConstructible
from xrlint.util.serializable import JsonSerializable

if TYPE_CHECKING:  # pragma: no cover
    from xrlint.config import ConfigObject
    from xrlint.rule import RuleMeta


@dataclass(frozen=True, kw_only=True)
class EditInfo(JsonSerializable):
    """Not used yet."""


@dataclass(frozen=True)
class Suggestion(ValueConstructible, JsonSerializable):
    desc: str
    """Description of the suggestion."""

    data: dict[str, None] | None = None
    """Data that can be referenced in the description."""

    fix: EditInfo | None = None
    """Not used yet."""

    @classmethod
    def _from_str(cls, value: str, value_name: str | None = None) -> "Suggestion":
        return Suggestion(value)


@dataclass()
class Message(JsonSerializable):
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
    """The EditInfo object of auto-fix.
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


@dataclass(kw_only=True)
class Result(JsonSerializable):
    """The aggregated information of linting a dataset."""

    config_object: Union["ConfigObject", None] = None
    """The configuration object that produced this result 
    together with `file_path`.
    """

    file_path: str = MISSING_DATASET_FILE_PATH
    """The absolute path to the file of this result.
    This is the string "<dataset>" if the file path is unknown
    (when you didn't pass the `file_path` option to the
    `xrlint.lint_dataset()` method).
    """

    messages: list[Message] = field(default_factory=list)
    """The array of message objects."""

    fixable_error_count: int = 0
    """The number of errors that can be fixed automatically
     by the fix constructor option.
     """

    fixable_warning_count: int = 0
    """The number of warnings that can be fixed automatically
     by the fix constructor option.
     """

    error_count: int = 0
    """The number of errors. This includes fixable errors
     and fatal errors.
     """

    fatal_error_count: int = 0
    """The number of fatal errors."""

    warning_count: int = 0
    """The number of warnings. This includes fixable warnings."""

    @classmethod
    def new(
        cls,
        config_object: Union["ConfigObject", None] = None,
        file_path: str | None = None,
        messages: list[Message] | None = None,
    ):
        result = Result(
            config_object=config_object,
            file_path=file_path or MISSING_DATASET_FILE_PATH,
            messages=messages or [],
        )
        for m in messages:
            result.warning_count += 1 if m.severity == SEVERITY_WARN else 0
            result.error_count += 1 if m.severity == SEVERITY_ERROR else 0
            result.fatal_error_count += 1 if m.fatal else 0
        return result

    def to_html(self) -> str:
        from xrlint.formatters.html import format_result

        return "\n".join(format_result(self))

    def _repr_html_(self) -> str:
        return self.to_html()

    def get_docs_url_for_rule(self, rule_id: str) -> str | None:
        from xrlint.config import split_config_spec

        plugin_name, rule_name = split_config_spec(rule_id)
        if plugin_name == CORE_PLUGIN_NAME or plugin_name == "xcube":
            return f"{CORE_DOCS_URL}#{rule_name}"
        try:
            plugin = self.config_object.get_plugin(plugin_name)
            rule = self.config_object.get_rule(rule_name)
            return rule.meta.docs_url or plugin.meta.docs_url
        except ValueError:
            return None


def get_rules_meta_for_results(results: list[Result]) -> dict[str, "RuleMeta"]:
    """Get all rule metadata from the list of `results`.

    Args:
        results: List of `Result` objects.

    Returns:
        A dictionary that maps unique rule names to `RuleMeta` objects.
    """
    rules_meta = {}
    for result in results:
        for message in result.messages:
            if message.rule_id:
                rule = result.config_object.get_rule(message.rule_id)
                rules_meta[message.rule_id] = rule.meta
    return rules_meta


@dataclass()
class ResultStats:
    """Utility for collecting simple statistics from results."""

    error_count: int = 0
    warning_count: int = 0
    result_count: int = 0

    def collect(self, results: Iterable[Result]) -> Iterable[Result]:
        """Collect statistics from `results`."""
        for result in results:
            self.error_count += result.error_count
            self.warning_count += result.warning_count
            self.result_count += 1
            yield result
