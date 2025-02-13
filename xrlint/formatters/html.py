#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

import html
from collections.abc import Iterable

from xrlint.constants import SEVERITY_CODE_TO_COLOR, SEVERITY_CODE_TO_NAME
from xrlint.formatter import FormatterContext, FormatterOp
from xrlint.formatters import registry
from xrlint.result import Message, Result, get_rules_meta_for_results
from xrlint.util.formatting import format_problems
from xrlint.util.schema import schema


@registry.define_formatter(
    "html",
    version="1.0.0",
    schema=schema(
        "object",
        properties=dict(
            with_meta=schema("boolean", default=False),
        ),
    ),
)
class Html(FormatterOp):
    def __init__(self, with_meta: bool = False):
        self.with_meta = with_meta

    def format(
        self,
        context: FormatterContext,
        results: Iterable[Result],
    ) -> str:
        results = list(results)  # get them all

        lines = [
            "<div>",
            "<h3>Results</h3>",
        ]
        for result in results:
            lines.extend(format_result(result))
        lines.append("</div>")

        if self.with_meta:
            rules_meta = get_rules_meta_for_results(results)
            lines.append("<div>")
            lines.append("<h3>Rules</h3>")
            for rm in rules_meta.values():
                lines.append(
                    f"<p>Rule <strong>{rm.name}</strong>, version {rm.version}</p>"
                )
                if rm.description:
                    lines.append(f"<p>{rm.description}</p>")
                if rm.docs_url:
                    lines.append(
                        f'<p><a href="{rm.docs_url}">Rule documentation</a></p>'
                    )
            lines.append("</div>")

        return HtmlText("\n".join(lines))


def format_result(result: Result) -> list[str]:
    lines = ['<div style="padding-bottom: 5px">']
    escaped_path = _format_file_path(result.file_path)
    if not result.messages:
        lines.append(
            f"<p>{escaped_path} - "
            f'<span style="font-weight:bold;color:green">ok</span>'
            f"</p>"
        )
    else:
        lines.append(
            f"<p>{escaped_path} - "
            f"<span>{format_problems(result.error_count, result.warning_count)}</span>"
            f"</p>"
        )
        lines.append("<hr/>")
        table_data = []
        for m in result.messages:
            table_data.append(
                [
                    _format_node_path(m),
                    _format_severity(m),
                    _format_message(m),
                    _format_rule_id(m, result),
                ]
            )
        lines.extend(_format_result_data(table_data))
    lines.append("</div>")
    return lines


def _format_file_path(file_path: str) -> str:
    return f'<span style="font-family:monospace;font-weight:bold">{html.escape(file_path)}</span>'


def _format_node_path(m: Message) -> str:
    if not m.node_path:
        return ""
    return f'<span style="font-family:monospace;font-size:0.7em">{m.node_path}</span>'


def _format_message(m: Message) -> str:
    return m.message


def _format_rule_id(m: Message, r: Result) -> str:
    if not m.rule_id:
        return ""
    docs_url = r.get_docs_url_for_rule(m.rule_id)
    if docs_url:
        return f'<a href="{docs_url}">{m.rule_id}</a>'
    return m.rule_id


def _format_severity(m: Message) -> str:
    if not m.severity:
        return ""
    name = SEVERITY_CODE_TO_NAME.get(m.severity)
    color = SEVERITY_CODE_TO_COLOR.get(m.severity)
    return f'<span style="color:{color}">{name}</span>'


def _format_result_data(data: list[list[str]]) -> list[str]:
    lines = ["<table>"]
    for row in data:
        lines.append("  <tr>")
        lines.extend(f'    <td  style="text-align:left">{value}</td>' for value in row)
        lines.append("  </tr>")
    lines.append("</table>")
    return lines


class HtmlText(str):
    """Allow displaying `text` as HTML in Jupyter notebooks."""

    def _repr_html_(self: str) -> str:
        """Represent HTML text as HTML."""
        return self
