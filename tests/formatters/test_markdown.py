from unittest import TestCase

import pytest

from xrlint.formatter import FormatterContext
from xrlint.formatters.markdown import Markdown
from .helpers import get_test_results


class MarkdownTest(TestCase):
    # noinspection PyMethodMayBeStatic
    def test_markdown(self):
        formatter = Markdown()
        with pytest.raises(NotImplementedError):
            formatter.format(
                context=FormatterContext(),
                results=get_test_results(),
            )
