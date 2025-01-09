from unittest import TestCase

import pytest

from xrlint.formatters.markdown import Markdown
from .helpers import get_test_results, get_context


class MarkdownTest(TestCase):
    # noinspection PyMethodMayBeStatic
    def test_markdown(self):
        formatter = Markdown()
        with pytest.raises(NotImplementedError):
            formatter.format(
                context=get_context(),
                results=get_test_results(),
            )
