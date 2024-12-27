from dataclasses import dataclass, field
import html

from tabulate import tabulate

from xrlint.constants import SEVERITY_CODE_TO_NAME
from xrlint.constants import SEVERITY_ERROR
from xrlint.constants import SEVERITY_WARN
from xrlint.rule import RuleMeta
from xrlint.rule_reg import RuleRegistry
from xrlint.message import Message
from xrlint.util.formatting import format_problems
from xrlint.util.todict import ToDictMixin


@dataclass(kw_only=True)
class Result(ToDictMixin):
    """The aggregated information of linting a dataset."""

    file_path: str
    """The absolute path to the file of this result. 
    This is the string "<file>" if the file path is unknown 
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
    def new(cls, file_path: str, messages: list[Message]):
        result = Result(file_path=file_path, messages=messages)
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


def get_rules_meta_for_results(
    results: list[Result], _registry: RuleRegistry | None = None
) -> dict[str, RuleMeta]:
    if _registry is None:
        from xrlint.rules import import_rules

        _registry = import_rules()
    rules_meta = {}
    for r in results:
        for m in r.messages:
            if m.rule_id:
                rule = _registry.lookup(m.rule_id)
                if rule is not None:
                    rules_meta[m.rule_id] = rule.meta
    return rules_meta
