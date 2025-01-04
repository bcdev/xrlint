from unittest import TestCase

from xrlint.node import XarrayNode


class XarrayNodeTest(TestCase):
    def node(self, path: str):
        return XarrayNode(path=path, parent=None)

    def attrs_node(self):
        return self.node("dataset.attrs")

    def coords_node(self):
        return self.node("dataset.coords['x']")

    def data_var_node(self):
        return self.node("dataset.data_vars['v']")

    def test_in_coords(self):
        self.assertEqual(False, self.attrs_node().in_coords())
        self.assertEqual(True, self.coords_node().in_coords())
        self.assertEqual(False, self.data_var_node().in_coords())

    def test_in_data_vars(self):
        self.assertEqual(False, self.attrs_node().in_data_vars())
        self.assertEqual(False, self.coords_node().in_data_vars())
        self.assertEqual(True, self.data_var_node().in_data_vars())

    def test_in_root(self):
        self.assertEqual(True, self.attrs_node().in_root())
        self.assertEqual(False, self.coords_node().in_root())
        self.assertEqual(False, self.data_var_node().in_root())
