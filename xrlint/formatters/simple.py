from xrlint.constants import SEVERITY_CODE_TO_NAME
from xrlint.formatter import FormatterOp, FormatterContext
from xrlint.formatters import registry
from xrlint.result import Result
from xrlint.util.formatting import format_problems, format_styled

from tabulate import tabulate

SEVERITY_CODE_TO_COLOR = {2: "red", 1: "blue", 0: "green", None: ""}
RULE_REF_URL = "https://bcdev.github.io/xrlint/rule-ref/"


@registry.define_formatter("simple", version="1.0.0")
class Simple(FormatterOp):

    def __init__(self, color_enabled: bool = False):
        self.color_enabled = color_enabled

    def format(
        self,
        context: FormatterContext,
        results: list[Result],
    ) -> str:
        text = []
        error_count = 0
        warning_count = 0
        for r in results:
            file_text = r.file_path
            if self.color_enabled:
                file_text = format_styled(file_text, s="underline")
            if not r.messages:
                text.append(f"\n{file_text} - ok\n")
            else:
                text.append(f"\n{file_text}:\n")
                r_data = []
                for m in r.messages:
                    node_text = m.node_path or ""
                    severity_text = SEVERITY_CODE_TO_NAME.get(m.severity, "?")
                    message_text = m.message or ""
                    rule_text = m.rule_id or ""
                    if self.color_enabled:
                        if node_text:
                            node_text = format_styled(node_text, s="dim")
                        if severity_text:
                            fg = SEVERITY_CODE_TO_COLOR.get(m.severity, "")
                            severity_text = format_styled(
                                severity_text, s="bold", fg=fg
                            )
                        if rule_text:
                            # TODO: get actual URL from metadata of the rule's plugin
                            href = f"{RULE_REF_URL}#{rule_text}"
                            rule_text = format_styled(m.rule_id, fg="blue", href=href)
                    r_data.append(
                        [
                            node_text,
                            severity_text,
                            message_text,
                            rule_text,
                        ]
                    )
                text.append(tabulate(r_data, headers=(), tablefmt="plain"))
                text.append("\n")
                error_count += r.error_count
                warning_count += r.warning_count
        problems_text = format_problems(error_count, warning_count)
        if self.color_enabled:
            if error_count:
                problems_text = format_styled(
                    problems_text, fg=SEVERITY_CODE_TO_COLOR[2]
                )
            elif warning_count:
                problems_text = format_styled(
                    problems_text, fg=SEVERITY_CODE_TO_COLOR[1]
                )
        text.append("\n")
        text.append(problems_text)
        text.append("\n")
        return "".join(text)
