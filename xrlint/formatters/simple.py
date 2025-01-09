from collections.abc import Iterable

from xrlint.constants import SEVERITY_CODE_TO_NAME
from xrlint.formatter import FormatterOp, FormatterContext
from xrlint.formatters import registry
from xrlint.result import Result
from xrlint.util.formatting import format_problems, format_styled

from tabulate import tabulate

from xrlint.util.schema import schema

SEVERITY_CODE_TO_COLOR = {2: "red", 1: "blue", 0: "green", None: ""}
RULE_REF_URL = "https://bcdev.github.io/xrlint/rule-ref/"


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

        summary_text = self.format_summary(error_count, warning_count)
        if self.output:
            print(summary_text, flush=True, end="")
        text_parts.append(summary_text)

        return "".join(text_parts)

    def format_result(
        self,
        result: Result,
    ) -> str:
        file_path_text = result.file_path
        if self.styled:
            file_path_text = format_styled(file_path_text, s="underline")
        if not result.messages:
            return f"\n{file_path_text} - ok\n"

        result_parts = [f"\n{file_path_text}:\n"]
        result_data = []
        for message in result.messages:
            node_text = message.node_path or ""
            severity_text = SEVERITY_CODE_TO_NAME.get(message.severity, "?")
            message_text = message.message or ""
            rule_text = message.rule_id or ""
            if self.styled:
                if node_text:
                    node_text = format_styled(node_text, s="dim")
                if severity_text:
                    fg = SEVERITY_CODE_TO_COLOR.get(message.severity, "")
                    severity_text = format_styled(severity_text, s="bold", fg=fg)
                if rule_text:
                    # TODO: get actual URL from metadata of the rule's plugin
                    href = f"{RULE_REF_URL}#{rule_text}"
                    rule_text = format_styled(message.rule_id, fg="blue", href=href)
            result_data.append(
                [
                    node_text,
                    severity_text,
                    message_text,
                    rule_text,
                ]
            )

        result_parts.append(tabulate(result_data, headers=(), tablefmt="plain"))
        result_parts.append("\n")
        return "".join(result_parts)

    def format_summary(self, error_count, warning_count) -> str:
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
