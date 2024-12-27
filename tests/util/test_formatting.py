from unittest import TestCase

from xrlint.util.formatting import format_count
from xrlint.util.formatting import format_problems


class FormattingTest(TestCase):
    def test_format_count(self):
        self.assertEqual("-3 eggs", format_count(-3, "egg"))
        self.assertEqual("-2 eggs", format_count(-2, "egg"))
        self.assertEqual("-1 eggs", format_count(-1, "egg"))
        self.assertEqual("no eggs", format_count(0, "egg"))
        self.assertEqual("one egg", format_count(1, "egg"))
        self.assertEqual("2 eggs", format_count(2, "egg"))
        self.assertEqual("3 eggs", format_count(3, "egg"))

    def test_format_problems(self):
        self.assertEqual("no problems", format_problems(0, 0))
        self.assertEqual("one error", format_problems(1, 0))
        self.assertEqual("2 errors", format_problems(2, 0))
        self.assertEqual("one warning", format_problems(0, 1))
        self.assertEqual(
            "2 problems (one error and one warning)", format_problems(1, 1)
        )
        self.assertEqual("3 problems (2 errors and one warning)", format_problems(2, 1))
        self.assertEqual("2 warnings", format_problems(0, 2))
        self.assertEqual("3 problems (one error and 2 warnings)", format_problems(1, 2))
        self.assertEqual("4 problems (2 errors and 2 warnings)", format_problems(2, 2))
