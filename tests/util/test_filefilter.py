#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

import unittest

from xrlint.util.filefilter import FileFilter
from xrlint.util.filepattern import FilePattern


class FileFilterTest(unittest.TestCase):
    def test_constructor(self):
        file_filter = FileFilter()
        self.assertEqual((), file_filter.files)
        self.assertEqual((), file_filter.ignores)

        files = (FilePattern("**/*.zarr"),)
        ignores = (FilePattern(".git"),)
        file_filter = FileFilter(files, ignores)
        self.assertIs(files, file_filter.files)
        self.assertIs(ignores, file_filter.ignores)

    def test_empty(self):
        file_filter = FileFilter()
        self.assertEqual(True, file_filter.empty)

        file_filter = FileFilter((), ())
        self.assertEqual(True, file_filter.empty)

        file_filter = FileFilter((), (FilePattern(".git"),))
        self.assertEqual(False, file_filter.empty)

        file_filter = FileFilter((FilePattern("**/*.zarr"),), ())
        self.assertEqual(False, file_filter.empty)

        file_filter = FileFilter((FilePattern("**/*.zarr"),), (FilePattern(".git"),))
        self.assertEqual(False, file_filter.empty)

    def test_from_patterns(self):
        self.assertEqual(FileFilter(), FileFilter.from_patterns(None, None))
        self.assertEqual(FileFilter(), FileFilter.from_patterns([], []))
        self.assertEqual(
            FileFilter((FilePattern("**/*.zarr"),), (FilePattern(".git"),)),
            FileFilter.from_patterns(["**/*.zarr"], [".git"]),
        )

    def test_merge(self):
        file_filter_1 = FileFilter((FilePattern("**/*.zarr"),), (FilePattern(".git"),))
        file_filter_2 = FileFilter((FilePattern("**/*.nc"),), (FilePattern("src/"),))
        self.assertEqual(
            FileFilter(
                (FilePattern("**/*.zarr"), FilePattern("**/*.nc")),
                (FilePattern(".git"), FilePattern("src/")),
            ),
            file_filter_1.merge(file_filter_2),
        )

    def test_accept(self):
        file_filter = FileFilter.from_patterns(["**/*.zarr"], None)
        self.assertEqual(True, file_filter.accept("test.zarr"))
        self.assertEqual(False, file_filter.accept("test.nc"))
        self.assertEqual(True, file_filter.accept("./temp/x.zarr"))

        file_filter = FileFilter.from_patterns(["**/*.zarr"], ["**/test.zarr"])
        self.assertEqual(False, file_filter.accept("test.zarr"))
        self.assertEqual(True, file_filter.accept("test-1.zarr"))
        self.assertEqual(True, file_filter.accept("test-2.zarr"))

        # negated ignores:
        file_filter = FileFilter.from_patterns(
            ["**/*.zarr"], ["**/temp/*", "!**/temp/x.zarr"]
        )
        self.assertEqual(True, file_filter.accept("./test.zarr"))
        self.assertEqual(True, file_filter.accept("./temp/x.zarr"))
        self.assertEqual(False, file_filter.accept("./temp/y.zarr"))

        # negated ignores:
        file_filter = FileFilter.from_patterns([], ["**/temp/*", "!**/temp/*.zarr"])
        self.assertEqual(True, file_filter.accept("./ds.nc"))
        self.assertEqual(True, file_filter.accept("./temp/ds.zarr"))
        self.assertEqual(True, file_filter.accept("./temp/test/ds.zarr"))
        self.assertEqual(False, file_filter.accept("./temp/ds.nc"))
        self.assertEqual(False, file_filter.accept("./temp/README.md"))

        # just ignores:
        file_filter = FileFilter.from_patterns([], ["**/*.json", "**/*.yaml"])
        self.assertEqual(True, file_filter.accept("./test.nc"))
        self.assertEqual(True, file_filter.accept("./temp/x.zarr"))
        self.assertEqual(False, file_filter.accept("c.yaml"))
        self.assertEqual(False, file_filter.accept("test/config.json"))
        self.assertEqual(False, file_filter.accept("test/config.yaml"))
