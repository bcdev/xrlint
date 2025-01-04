import unittest

from xrlint.util.minimatch import minimatch


class MinimatchTest(unittest.TestCase):
    def test_no_magic(self):
        pattern = ""
        self.assertEqual(True, minimatch("file", pattern))
        self.assertEqual(True, minimatch("dir1/", pattern))
        self.assertEqual(True, minimatch("dir1/fod", pattern))
        self.assertEqual(True, minimatch("dir1/dir2/fod", pattern))

        pattern = "fod"
        self.assertEqual(True, minimatch("fod", pattern))
        self.assertEqual(True, minimatch("fod/", pattern))
        self.assertEqual(False, minimatch("dir1/fod", pattern))
        self.assertEqual(False, minimatch("dir1/dir2/fod", pattern))

        pattern = "dir1/"
        self.assertEqual(True, minimatch("dir1", pattern))
        self.assertEqual(True, minimatch("dir1/", pattern))
        self.assertEqual(False, minimatch("dir1/fod", pattern))
        self.assertEqual(False, minimatch("dir1/dir2/fod", pattern))

    def test_question_mark_magic(self):
        pattern = "dir?/fod"
        self.assertEqual(True, minimatch("dir1/fod", pattern))
        self.assertEqual(True, minimatch("dir2/fod", pattern))
        self.assertEqual(False, minimatch("dir/fod", pattern))

        pattern = "fod.???"
        self.assertEqual(True, minimatch("fod.ext", pattern))
        self.assertEqual(True, minimatch("fod.tif", pattern))
        self.assertEqual(False, minimatch("fod.py", pattern))
        self.assertEqual(False, minimatch("fod.zarr", pattern))

    def test_star_magic(self):
        pattern = "*"
        self.assertEqual(True, minimatch("fod", pattern))
        self.assertEqual(True, minimatch("fod.ext", pattern))
        self.assertEqual(True, minimatch("dir1/", pattern))
        self.assertEqual(True, minimatch("dir1.ext/", pattern))
        self.assertEqual(False, minimatch("dir1/fod", pattern))
        self.assertEqual(False, minimatch("dir1/dir2/fod", pattern))

        pattern = "*.ext"
        self.assertEqual(True, minimatch("fod.ext", pattern))
        self.assertEqual(True, minimatch("fod.ext/", pattern))
        self.assertEqual(False, minimatch("fod.ext2", pattern))
        self.assertEqual(False, minimatch("dir1/fod.ext", pattern))

        pattern = "fod.*"
        self.assertEqual(True, minimatch("fod.ext", pattern))
        self.assertEqual(True, minimatch("fod.ext/", pattern))
        self.assertEqual(True, minimatch("fod.ext2", pattern))
        self.assertEqual(False, minimatch("dir1/fod.ext", pattern))

        pattern = "dir1/*"
        self.assertEqual(False, minimatch("dir1", pattern))
        self.assertEqual(False, minimatch("dir1/", pattern))
        self.assertEqual(True, minimatch("dir1/fod", pattern))
        self.assertEqual(False, minimatch("dir1/dir2/fod", pattern))

        pattern = "*/fod"
        self.assertEqual(False, minimatch("fod", pattern))
        self.assertEqual(False, minimatch("fod/", pattern))
        self.assertEqual(True, minimatch("dir1/fod", pattern))
        self.assertEqual(False, minimatch("dir1/dir2/fod", pattern))

        pattern = "fod*"
        self.assertEqual(True, minimatch("fod", pattern))
        self.assertEqual(False, minimatch("fod/dir2", pattern))

        pattern = "dir*/fod"
        self.assertEqual(True, minimatch("dir/fod", pattern))
        self.assertEqual(True, minimatch("dir1/fod", pattern))

        pattern = "dir1/*/fod"
        self.assertEqual(False, minimatch("fod", pattern))
        self.assertEqual(False, minimatch("fod/", pattern))
        self.assertEqual(False, minimatch("dir1/fod", pattern))
        self.assertEqual(True, minimatch("dir1/dir2/fod", pattern))

        pattern = "*/*/*/*.ext"
        self.assertEqual(False, minimatch("fod.ext", pattern))
        self.assertEqual(False, minimatch("dir1/fod.ext", pattern))
        self.assertEqual(False, minimatch("dir1/dir2/fod.ext", pattern))
        self.assertEqual(True, minimatch("dir1/dir2/dir3/fod.ext", pattern))
        self.assertEqual(False, minimatch("dir1/dir2/dir3/dir4/fod.ext", pattern))

    def test_glob_star_magic(self):
        pattern = "**"
        self.assertEqual(True, minimatch("fod", pattern))
        self.assertEqual(True, minimatch("fod.ext", pattern))
        self.assertEqual(True, minimatch("dir1/", pattern))
        self.assertEqual(True, minimatch("dir1.ext/", pattern))
        self.assertEqual(True, minimatch("dir1/fod", pattern))
        self.assertEqual(True, minimatch("dir1/dir2/fod", pattern))

        pattern = "**.ext"
        self.assertEqual(True, minimatch("fod.ext", pattern))
        self.assertEqual(True, minimatch("fod.ext/", pattern))
        self.assertEqual(False, minimatch("fod.ext2", pattern))
        self.assertEqual(True, minimatch("dir1/fod.ext", pattern))

        pattern = "fod.**"
        self.assertEqual(True, minimatch("fod.ext", pattern))
        self.assertEqual(True, minimatch("fod.ext/", pattern))
        self.assertEqual(True, minimatch("fod.ext2", pattern))
        self.assertEqual(True, minimatch("fod.ext2/dir2", pattern))
        self.assertEqual(False, minimatch("dir1/fod.ext", pattern))
        self.assertEqual(False, minimatch("dir1/fod.ext/dir3", pattern))

        pattern = "dir1/**"
        self.assertEqual(False, minimatch("dir1", pattern))
        self.assertEqual(False, minimatch("dir1/", pattern))
        self.assertEqual(True, minimatch("dir1/fod", pattern))
        self.assertEqual(True, minimatch("dir1/dir2/fod", pattern))

        pattern = "**/fod"
        self.assertEqual(True, minimatch("fod", pattern))
        self.assertEqual(True, minimatch("fod/", pattern))
        self.assertEqual(True, minimatch("dir1/fod", pattern))
        self.assertEqual(True, minimatch("dir1/dir2/fod", pattern))
        self.assertEqual(True, minimatch("dir1/dir2/dir3/fod", pattern))

        pattern = "dir1/**/fod"
        self.assertEqual(False, minimatch("fod", pattern))
        self.assertEqual(False, minimatch("fod/", pattern))
        self.assertEqual(True, minimatch("dir1/fod", pattern))
        self.assertEqual(True, minimatch("dir1/dir2/fod", pattern))
        self.assertEqual(True, minimatch("dir1/dir2/dir3/fod", pattern))

    def test_extension_pattern(self):
        pattern = "**/*.ext"
        self.assertEqual(True, minimatch("fod.ext", pattern))
        self.assertEqual(True, minimatch("dir1/fod.ext", pattern))
        self.assertEqual(True, minimatch("dir1/dir2/fod.ext", pattern))
        self.assertEqual(True, minimatch("/fod.ext", pattern))
        self.assertEqual(True, minimatch("/dir1/dir2/fod.ext", pattern))
        self.assertEqual(False, minimatch("fod.nc", pattern))
        self.assertEqual(False, minimatch("dir1/dir2/fod.nc", pattern))
