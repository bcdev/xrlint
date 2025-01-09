from collections.abc import Iterable

from xrlint.formatter import FormatterOp, FormatterContext
from xrlint.formatters import registry
from xrlint.result import Result


@registry.define_formatter("markdown", version="1.0.0")
class Markdown(FormatterOp):

    def format(
        self,
        context: FormatterContext,
        results: Iterable[Result],
    ) -> str:
        # TODO: implement "markdown" format
        raise NotImplementedError()
