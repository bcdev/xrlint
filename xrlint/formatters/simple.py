from xrlint.constants import SEVERITY_CODE_TO_NAME
from xrlint.formatter import FormatterOp, FormatterContext
from xrlint.formatters import registry
from xrlint.result import Result
from xrlint.util.formatting import format_problems, format_link, format_styled

from tabulate import tabulate


@registry.define_formatter("simple", version="1.0.0")
class Simple(FormatterOp):

    def format(
        self,
        context: FormatterContext,
        results: list[Result],
    ) -> str:
        text = []
        error_count = 0
        warning_count = 0
        for r in results:
            if not r.messages:
                text.append(f"\n{r.file_path} - ok\n")
            else:
                text.append(f"\n{r.file_path}:\n")
                r_data = []
                for m in r.messages:
                    severity = SEVERITY_CODE_TO_NAME.get(m.severity)
                    docs_url = "https://bcdev.github.io/xrlint"
                    r_data.append(
                        [
                            m.node_path,
                            format_styled(severity, s=3, fg=31 if m.severity == 2 else 32),
                            m.message,
                            format_styled(format_link(docs_url, m.rule_id), s=2, fg=34),
                        ]
                    )
                text.append(tabulate(r_data, headers=(), tablefmt="plain"))
                text.append("\n")
                error_count += r.error_count
                warning_count += r.warning_count
        text.append("\n")
        text.append(format_problems(error_count, warning_count))
        text.append("\n")
        return "".join(text)
