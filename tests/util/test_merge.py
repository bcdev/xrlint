from unittest import TestCase

from xrlint.util.merge import merge_arrays
from xrlint.util.merge import merge_dicts
from xrlint.util.merge import merge_set_lists
from xrlint.util.merge import merge_values


class NamingTest(TestCase):
    def test_merge_arrays(self):
        self.assertEqual(None, merge_arrays(None, None))
        self.assertEqual(["x"], merge_arrays(["x"], None))
        self.assertEqual(["y"], merge_arrays(None, ["y"]))
        self.assertEqual(["y"], merge_arrays(["x"], ["y"]))
        self.assertEqual(["z", "y"], merge_arrays(["x", "y"], ["z"]))
        self.assertEqual(["y", "z"], merge_arrays(["x"], ["y", "z"]))

    def test_merge_dicts(self):
        self.assertEqual(None, merge_dicts(None, None))
        self.assertEqual({"x": 1}, merge_dicts({"x": 1}, None))
        self.assertEqual({"y": 2}, merge_dicts(None, {"y": 2}))
        self.assertEqual({"x": 1, "y": 2}, merge_dicts({"x": 1}, {"y": 2}))
        self.assertEqual({"x": 2}, merge_dicts({"x": 1}, {"x": 2}))
        self.assertEqual(
            {"x": 1, "y": 2, "z": 3}, merge_dicts({"x": 1, "y": 2}, {"z": 3})
        )

    def test_merge_set_lists(self):
        self.assertEqual(None, merge_set_lists(None, None))
        self.assertEqual(["y"], merge_set_lists(None, ["y"]))
        self.assertEqual(["x"], merge_set_lists(["x"], None))
        self.assertEqual(["x", "y"], merge_set_lists(["x"], ["y"]))
        self.assertEqual(["y", "x"], merge_set_lists(["y", "x"], ["x", "y"]))

    def test_merge_values(self):
        self.assertEqual(None, merge_values(None, None))
        self.assertEqual(["z", "y"], merge_values(["x", "y"], ["z"]))
        self.assertEqual({"x": 1, "y": 2}, merge_values({"x": 1}, {"y": 2}))
        self.assertEqual(1, merge_values("x", 1))
        self.assertEqual(2, merge_values(["x"], 2))
        self.assertEqual(3, merge_values({"x": 1}, 3))
