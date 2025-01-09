from collections.abc import Iterable

from xrlint.formatter import FormatterOp, FormatterContext
from xrlint.formatters import registry
from xrlint.result import Result, get_rules_meta_for_results
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

        text_parts = [
            '<div role="results">\n',
            "<h3>Results</h3>\n",
        ]

        for i, result in enumerate(results):
            if i > 0:
                text_parts.append("<hr/>\n")
            text_parts.append('<div role="result">\n')
            text_parts.append(result.to_html())
            text_parts.append("</div>\n")
        text_parts.append("</div>\n")

        if self.with_meta:
            rules_meta = get_rules_meta_for_results(results)
            text_parts.append('<div role="rules_meta">\n')
            text_parts.append("<h3>Rules</h3>\n")
            for rm in rules_meta.values():
                text_parts.append(
                    f"<p>Rule <strong>{rm.name}</strong>, version {rm.version}</p>\n"
                )
                if rm.description:
                    text_parts.append(f"<p>{rm.description}</p>\n")
                if rm.docs_url:
                    text_parts.append(
                        f'<p><a href="{rm.docs_url}">Rule documentation</a></p>\n'
                    )
            text_parts.append("</div>\n")

        return "".join(text_parts)
