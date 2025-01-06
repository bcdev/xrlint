import dataclasses
import math
import unittest
from functools import cached_property

from xrlint.util.todict import ToDictMixin


@dataclasses.dataclass
class Point(ToDictMixin):
    x: float
    y: float

    @property
    def mh_dist(self) -> float:
        return abs(self.x) + abs(self.y)

    @cached_property
    def dist(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y)

    def is_origin(self, eps: float = 1e-10) -> float:
        return self.dist < eps


class ToDictMixinTest(unittest.TestCase):
    def test_to_dict_includes_only_data_fields(self):
        self.assertEqual({"x": 12, "y": 32}, Point(12, 32).to_dict())

    def test_to_dict_excludes_none(self):
        # noinspection PyTypeChecker
        self.assertEqual({"x": 12}, Point(12, None).to_dict())

    def test_str_includes_only_data_fields(self):
        self.assertEqual("Point(x=13, y=21)", str(Point(13, 21)))
        self.assertEqual("Point(x=13, y=21)", repr(Point(13, 21)))
