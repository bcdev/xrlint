import json

from xrlint.formatter import FormatterOp, FormatterContext
from xrlint.result import Result, get_rules_meta_for_results
from xrlint.formatters import registry
from xrlint.util.schema import schema


@registry.define_formatter(
    "json",
    version="1.0.0",
    schema=schema(
        "object",
        properties=dict(
            indent=schema("integer", minimum=0, maximum=8, default=2),
            with_meta=schema("boolean", default=False),
        ),
    ),
)
class Json(FormatterOp):

    def __init__(self, indent: int = 2, with_meta: bool = False):
        super().__init__()
        self.indent = indent
        self.with_meta = with_meta

    def format(
        self,
        context: FormatterContext,
        results: list[Result],
    ) -> str:
        omitted_props = {"config"}
        results_json = {
            "results": [
                {k: v for k, v in r.to_dict().items() if k not in omitted_props}
                for r in results
            ],
        }
        if self.with_meta:
            rules_meta = get_rules_meta_for_results(results)
            results_json.update(
                {
                    "rules_meta": [rm.to_dict() for rm in rules_meta.values()],
                }
            )
        return json.dumps(results_json, indent=self.indent)
