from unittest import TestCase

from xrlint.util.registry import Registry


class RegistryTest(TestCase):
    def test_it(self):
        r = Registry[int]()
        self.assertEqual({}, r.as_dict())
        r.register("a", 1)
        r.register("b", 2)
        self.assertEqual({"a": 1, "b": 2}, r.as_dict())
        self.assertEqual(1, r.lookup("a"))
        self.assertEqual(2, r.lookup("b"))
        self.assertEqual(None, r.lookup("c"))
