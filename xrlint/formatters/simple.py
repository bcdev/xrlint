#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from collections.abc import Iterable

from tabulate import tabulate

from xrlint.constants import SEVERITY_CODE_TO_COLOR, SEVERITY_CODE_TO_NAME
from xrlint.formatter import FormatterContext, FormatterOp
from xrlint.formatters import registry
from xrlint.result import Message, Result
from xrlint.util.formatting import format_problems, format_styled
from xrlint.util.schema import schema


@registry.define_formatter(
    "simple",
    version="1.0.0",
    schema=schema(
        "object",
        properties=dict(
            styled=schema("boolean", default=True),
            output=schema("boolean", default=True),
        ),
    ),
)
class Simple(FormatterOp):
    """Simple output formatter.
    Produces either ANSI-styled (default) or plain text reports.
    It incrementally outputs results to console (stdout) by default.
    """

    def __init__(self, styled: bool = True, output: bool = True):
        self.styled = styled
        self.output = output

    def format(
        self,
        context: FormatterContext,
        results: Iterable[Result],
    ) -> str:
        text_parts = []

        error_count = 0
        warning_count = 0
        for result in results:
            result_text = self.format_result(result)
            if self.output:
                print(result_text, flush=True, end="")
            text_parts.append(result_text)
            error_count += result.error_count
            warning_count += result.warning_count

        summary_text = self._format_summary(error_count, warning_count)
        if self.output:
            print(summary_text, flush=True, end="")
        text_parts.append(summary_text)

        return "".join(text_parts)

    def format_result(
        self,
        result: Result,
    ) -> str:
        file_path_text = self._format_file_path(result)
        if not result.messages:
            return f"\n{file_path_text} - ok\n"
        result_parts = [f"\n{file_path_text}:\n"]
        result_data = []
        for message in result.messages:
            result_data.append(
                [
                    self._format_node_path(message),
                    self._format_severity(message),
                    self._format_message(message),
                    self._format_rule_id(message, result),
                ]
            )
        result_parts.append(tabulate(result_data, headers=(), tablefmt="plain"))
        result_parts.append("\n")
        return "".join(result_parts)

    def _format_file_path(self, result) -> str:
        file_path_text = result.file_path
        if self.styled:
            file_path_text = format_styled(file_path_text, s="underline")
        return file_path_text

    def _format_node_path(self, m: Message) -> str:
        node_text = m.node_path or ""
        if self.styled and node_text:
            node_text = format_styled(node_text, s="dim")
        return node_text

    def _format_severity(self, m: Message) -> str:
        severity_text = SEVERITY_CODE_TO_NAME.get(m.severity, "?")
        if self.styled and severity_text:
            fg = SEVERITY_CODE_TO_COLOR.get(m.severity, "")
            severity_text = format_styled(severity_text, s="bold", fg=fg)
        return severity_text

    # noinspection PyMethodMayBeStatic
    def _format_message(self, m: Message) -> str:
        return m.message or ""

    def _format_rule_id(self, m: Message, r: Result) -> str:
        rule_text = m.rule_id or ""
        if self.styled and rule_text:
            rule_url = r.get_docs_url_for_rule(m.rule_id)
            if rule_url:
                rule_text = format_styled(rule_text, fg="blue", href=rule_url)
        return rule_text

    def _format_summary(self, error_count, warning_count) -> str:
        summary_parts = []
        problems_text = format_problems(error_count, warning_count)
        if self.styled:
            if error_count:
                problems_text = format_styled(
                    problems_text, fg=SEVERITY_CODE_TO_COLOR[2]
                )
            elif warning_count:
                problems_text = format_styled(
                    problems_text, fg=SEVERITY_CODE_TO_COLOR[1]
                )
        summary_parts.append("\n")
        summary_parts.append(problems_text)
        summary_parts.append("\n\n")
        return "".join(summary_parts)
