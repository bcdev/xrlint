#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from unittest import TestCase

from xrlint.plugins.xcube.util import is_absolute_path
from xrlint.plugins.xcube.util import resolve_path


class UtilTest(TestCase):
    def test_is_absolute_path(self):
        self.assertTrue(is_absolute_path("/home/forman"))
        self.assertTrue(is_absolute_path("//bcserver2/fs1"))
        self.assertTrue(is_absolute_path("file://home/forman"))
        self.assertTrue(is_absolute_path("s3://xcube-data"))
        self.assertTrue(is_absolute_path(r"C:\Users\Norman"))
        self.assertTrue(is_absolute_path(r"C:/Users/Norman"))
        self.assertTrue(is_absolute_path(r"C:/Users/Norman"))
        self.assertTrue(is_absolute_path(r"\\bcserver2\fs1"))

        self.assertFalse(is_absolute_path(r"data"))
        self.assertFalse(is_absolute_path(r"./data"))
        self.assertFalse(is_absolute_path(r"../data"))

    def test_resolve_path(self):
        self.assertEqual(
            "/home/forman/data", resolve_path("data", root_path="/home/forman")
        )
        self.assertEqual(
            "/home/forman/data", resolve_path("./data", root_path="/home/forman")
        )
        self.assertEqual(
            "/home/data", resolve_path("../data", root_path="/home/forman")
        )
        self.assertEqual("s3://opensr/test.zarr", resolve_path("s3://opensr/test.zarr"))
