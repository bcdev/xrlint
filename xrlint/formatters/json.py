import json

import xrlint.api as xrl
from xrlint.util.schema import schema
from xrlint.formatters import registry


@registry.define_formatter(
    name="json",
    version="1.0.0",
    schema=[
        schema("integer", minimum=0, maximum=8, default=4),
        schema("boolean", default=False),
    ],
)
class Json(xrl.FormatterOp):

    def __init__(self, indent: int = 2, with_meta: bool = False):
        super().__init__()
        self.indent = indent
        self.with_meta = with_meta

    def format(
        self,
        context: xrl.FormatterContext,
        results: list[xrl.Result],
    ) -> str:
        results_json = {
            "results": [r.to_dict() for r in results],
        }
        if self.with_meta:
            rules_meta = xrl.get_rules_meta_for_results(results)
            results_json.update({
                "rules_meta": [rm.to_dict() for rm in rules_meta.values()],
            })
        return json.dumps(results_json, indent=self.indent)
