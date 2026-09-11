#  Copyright © 2026 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from unittest import TestCase

import xarray as xr

from xrlint.node import DatasetNode, DataTreeNode
from xrlint.util.attrs import hierarchical_attrs


class HierarchicalAttrsTest(TestCase):
    def test_hierarchical_attrs(self):
        root_node = DataTreeNode(
            parent=None,
            path="dt",
            name="dt",
            datatree=xr.DataTree(
                dataset=xr.Dataset(attrs={"title": "root", "history": "root"})
            ),
        )
        dataset_node = DatasetNode(
            parent=root_node,
            path="dt/group",
            name="group",
            dataset=xr.Dataset(attrs={"title": "dataset"}),
        )

        attrs = hierarchical_attrs(dataset_node)

        self.assertEqual("dataset", attrs["title"])
        self.assertEqual("root", attrs["history"])
        self.assertEqual(["title", "history"], list(attrs))
        self.assertEqual(2, len(attrs))
        self.assertNotIn("comment", attrs)
        with self.assertRaises(KeyError):
            attrs["comment"]
