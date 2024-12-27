from unittest import TestCase

from xrlint.constants import SEVERITY_CODE_TO_NAME
from xrlint.constants import SEVERITY_ENUM
from xrlint.constants import SEVERITY_ENUM_TEXT


class ConstantsTest(TestCase):
    def test_computed_values(self):
        self.assertEqual({0: "off", 1: "warn", 2: "error"}, SEVERITY_CODE_TO_NAME)
        self.assertEqual(
            {"off": 0, "warn": 1, "error": 2, 0: 0, 1: 1, 2: 2},
            SEVERITY_ENUM,
        )
        self.assertEqual("'error', 'warn', 'off', 2, 1, 0", SEVERITY_ENUM_TEXT)
