import xrlint.api as xrl
from xrlint.constants import SEVERITY_CODE_TO_NAME
from xrlint.util.formatting import format_problems
from xrlint.formatters import registry


from tabulate import tabulate


@registry.define_formatter("simple", version="1.0.0")
class Simple(xrl.FormatterOp):

    def format(
        self,
        context: xrl.FormatterContext,
        results: list[xrl.Result],
    ) -> str:
        text = []
        for r in results:
            if not r.messages:
                text.append(f"{r.file_path} - ok\n")
            else:
                text.append(f"{r.file_path}:\n\n")
                r_data = []
                for m in r.messages:
                    r_data.append(
                        [
                            m.node_path,
                            SEVERITY_CODE_TO_NAME.get(m.severity),
                            m.message,
                            m.rule_id,
                        ]
                    )
                text.append(tabulate(r_data, headers=(), tablefmt="plain"))
                text.append(format_problems(r.error_count, r.warning_count))
                text.append("\n")
        return "".join(text)
