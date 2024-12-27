import xrlint.api as xrl
from xrlint.formatters import registry
from xrlint.util.schema import schema


@registry.define_formatter(
    name="html",
    version="1.0.0",
    schema=schema(
        "object",
        properties=dict(
            with_meta=schema("boolean", default=False),
        ),
    ),
)
class Html(xrl.FormatterOp):

    def __init__(self, with_meta: bool = False):
        self.with_meta = with_meta

    def format(
        self,
        context: xrl.FormatterContext,
        results: list[xrl.Result],
    ) -> str:
        text = []
        n = len(results)

        text.append('<div role="results">\n')
        text.append("<h3>Results</h3>\n")
        for i, r in enumerate(results):
            text.append('<div role="result">\n')
            text.append(r.to_html())
            text.append("</div>\n")
            if i < n - 1:
                text.append("<hr/>\n")
        text.append("</div>\n")

        if self.with_meta:
            rules_meta = xrl.get_rules_meta_for_results(results)
            text.append('<div role="rules_meta">\n')
            text.append("<h3>Rules</h3>\n")
            for rm in rules_meta.values():
                # TODO - output rule description
                text.append(f"<p>{rm.name}, version {rm.version}</p>\n")
            text.append("</div>\n")

        return "".join(text)
