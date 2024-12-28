import xrlint.api as xrl
from xrlint.formatters import registry


@registry.define_formatter("markdown", version="1.0.0")
class Markdown(xrl.FormatterOp):

    def format(
        self,
        context: xrl.FormatterContext,
        results: list[xrl.Result],
    ) -> str:
        # TODO: implement "markdown" format
        raise NotImplementedError()
