import unittest

from xrlint.util.filepattern import FilePattern


class MinimatchTest(unittest.TestCase):
    def test_basics(self):
        matcher = FilePattern("**/*.h5")
        self.assertEqual("**/*.h5", str(matcher))
        self.assertEqual("FilePattern('**/*.h5')", repr(matcher))
        self.assertTrue(matcher == matcher)
        self.assertFalse(matcher == 5)
        self.assertTrue(matcher == FilePattern("**/*.h5"))
        self.assertFalse(matcher == FilePattern("**/*.nc"))
        self.assertFalse(matcher != FilePattern("**/*.h5"))
        self.assertTrue(matcher != FilePattern("**/*.nc"))
        self.assertTrue(hash(matcher) == hash("**/*.h5"))

    def test_no_magic(self):
        matcher = FilePattern("fod")
        self.assertEqual(True, matcher.match("fod"))
        self.assertEqual(True, matcher.match("fod/"))
        self.assertEqual(False, matcher.match("dir1/fod"))
        self.assertEqual(False, matcher.match("dir1/dir2/fod"))

        matcher = FilePattern("dir1/")
        self.assertEqual(True, matcher.match("dir1"))
        self.assertEqual(True, matcher.match("dir1/"))
        self.assertEqual(False, matcher.match("dir1/fod"))
        self.assertEqual(False, matcher.match("dir1/dir2/fod"))

    def test_question_mark_magic(self):
        matcher = FilePattern("dir?/fod")
        self.assertEqual(True, matcher.match("dir1/fod"))
        self.assertEqual(True, matcher.match("dir2/fod"))
        self.assertEqual(False, matcher.match("dir/fod"))

        matcher = FilePattern("fod.???")
        self.assertEqual(True, matcher.match("fod.ext"))
        self.assertEqual(True, matcher.match("fod.tif"))
        self.assertEqual(False, matcher.match("fod.py"))
        self.assertEqual(False, matcher.match("fod.zarr"))

    def test_star_magic(self):
        matcher = FilePattern("*")
        self.assertEqual(True, matcher.match("fod"))
        self.assertEqual(True, matcher.match("fod.ext"))
        self.assertEqual(True, matcher.match("dir1/"))
        self.assertEqual(True, matcher.match("dir1.ext/"))
        self.assertEqual(False, matcher.match("dir1/fod"))
        self.assertEqual(False, matcher.match("dir1/dir2/fod"))

        matcher = FilePattern("*.ext")
        self.assertEqual(True, matcher.match("fod.ext"))
        self.assertEqual(True, matcher.match("fod.ext/"))
        self.assertEqual(False, matcher.match("fod.ext2"))
        self.assertEqual(False, matcher.match("dir1/fod.ext"))

        matcher = FilePattern("fod.*")
        self.assertEqual(True, matcher.match("fod.ext"))
        self.assertEqual(True, matcher.match("fod.ext/"))
        self.assertEqual(True, matcher.match("fod.ext2"))
        self.assertEqual(False, matcher.match("dir1/fod.ext"))

        matcher = FilePattern("dir1/*")
        self.assertEqual(False, matcher.match("dir1"))
        self.assertEqual(False, matcher.match("dir1/"))
        self.assertEqual(True, matcher.match("dir1/fod"))
        self.assertEqual(False, matcher.match("dir1/dir2/fod"))

        matcher = FilePattern("*/fod")
        self.assertEqual(False, matcher.match("fod"))
        self.assertEqual(False, matcher.match("fod/"))
        self.assertEqual(True, matcher.match("dir1/fod"))
        self.assertEqual(False, matcher.match("dir1/dir2/fod"))

        matcher = FilePattern("fod*")
        self.assertEqual(True, matcher.match("fod"))
        self.assertEqual(False, matcher.match("fod/dir2"))

        matcher = FilePattern("dir*/fod")
        self.assertEqual(True, matcher.match("dir/fod"))
        self.assertEqual(True, matcher.match("dir1/fod"))

        matcher = FilePattern("dir1/*/fod")
        self.assertEqual(False, matcher.match("fod"))
        self.assertEqual(False, matcher.match("fod/"))
        self.assertEqual(False, matcher.match("dir1/fod"))
        self.assertEqual(True, matcher.match("dir1/dir2/fod"))

        matcher = FilePattern("*/*/*/*.ext")
        self.assertEqual(False, matcher.match("fod.ext"))
        self.assertEqual(False, matcher.match("dir1/fod.ext"))
        self.assertEqual(False, matcher.match("dir1/dir2/fod.ext"))
        self.assertEqual(True, matcher.match("dir1/dir2/dir3/fod.ext"))
        self.assertEqual(False, matcher.match("dir1/dir2/dir3/dir4/fod.ext"))

    def test_glob_star_magic(self):
        matcher = FilePattern("**")
        self.assertEqual(True, matcher.match("fod"))
        self.assertEqual(True, matcher.match("fod.ext"))
        self.assertEqual(True, matcher.match("dir1/"))
        self.assertEqual(True, matcher.match("dir1.ext/"))
        self.assertEqual(True, matcher.match("dir1/fod"))
        self.assertEqual(True, matcher.match("dir1/dir2/fod"))

        matcher = FilePattern("**.ext")
        self.assertEqual(True, matcher.match("fod.ext"))
        self.assertEqual(True, matcher.match("fod.ext/"))
        self.assertEqual(False, matcher.match("fod.ext2"))
        self.assertEqual(True, matcher.match("dir1/fod.ext"))

        matcher = FilePattern("fod.**")
        self.assertEqual(True, matcher.match("fod.ext"))
        self.assertEqual(True, matcher.match("fod.ext/"))
        self.assertEqual(True, matcher.match("fod.ext2"))
        self.assertEqual(True, matcher.match("fod.ext2/dir2"))
        self.assertEqual(False, matcher.match("dir1/fod.ext"))
        self.assertEqual(False, matcher.match("dir1/fod.ext/dir3"))

        matcher = FilePattern("dir1/**")
        self.assertEqual(False, matcher.match("dir1"))
        self.assertEqual(False, matcher.match("dir1/"))
        self.assertEqual(True, matcher.match("dir1/fod"))
        self.assertEqual(True, matcher.match("dir1/dir2/fod"))

        matcher = FilePattern("**/fod")
        self.assertEqual(True, matcher.match("fod"))
        self.assertEqual(True, matcher.match("fod/"))
        self.assertEqual(True, matcher.match("dir1/fod"))
        self.assertEqual(True, matcher.match("dir1/dir2/fod"))
        self.assertEqual(True, matcher.match("dir1/dir2/dir3/fod"))

        matcher = FilePattern("dir1/**/fod")
        self.assertEqual(False, matcher.match("fod"))
        self.assertEqual(False, matcher.match("fod/"))
        self.assertEqual(True, matcher.match("dir1/fod"))
        self.assertEqual(True, matcher.match("dir1/dir2/fod"))
        self.assertEqual(True, matcher.match("dir1/dir2/dir3/fod"))

    def test_extension_pattern(self):
        matcher = FilePattern("**/*.ext")
        self.assertEqual(True, matcher.match("fod.ext"))
        self.assertEqual(True, matcher.match("dir1/fod.ext"))
        self.assertEqual(True, matcher.match("dir1/dir2/fod.ext"))
        self.assertEqual(True, matcher.match("/fod.ext"))
        self.assertEqual(True, matcher.match("/dir1/dir2/fod.ext"))
        self.assertEqual(False, matcher.match("fod.nc"))
        self.assertEqual(False, matcher.match("dir1/dir2/fod.nc"))

    def test_special_ops(self):
        matcher = FilePattern("")
        self.assertEqual(True, matcher.empty)
        self.assertEqual(True, matcher.match("file"))
        self.assertEqual(True, matcher.match("dir1/"))
        self.assertEqual(True, matcher.match("dir1/fod"))
        self.assertEqual(True, matcher.match("dir1/dir2/fod"))

        matcher = FilePattern("# comment")
        self.assertEqual(True, matcher.comment)
        self.assertEqual(False, matcher.match("fod"))
        self.assertEqual(False, matcher.match("# comment"))

        matcher = FilePattern("!**/.ext")
        self.assertEqual(True, matcher.negate)
        self.assertEqual(False, matcher.match("fod.ext"))
        self.assertEqual(True, matcher.match("fod.ex"))
        self.assertEqual(True, matcher.match("dir1.ex/dir2"))

        matcher = FilePattern("!**/.ext", flip_negate=True)
        self.assertEqual(True, matcher.negate)
        self.assertEqual(True, matcher.match("fod.ext"))
        self.assertEqual(False, matcher.match("fod.ex"))
        self.assertEqual(False, matcher.match("dir1.ex/dir2"))

        matcher = FilePattern("!!**/.ext")
        self.assertEqual(False, matcher.negate)
        self.assertEqual(True, matcher.match("fod.ext"))
        self.assertEqual(False, matcher.match("fod.ex"))
        self.assertEqual(False, matcher.match("dir1.ex/dir2"))

        matcher = FilePattern("dir/")
        self.assertEqual(True, matcher.dir)
        self.assertEqual(True, matcher.match("dir"))
        self.assertEqual(True, matcher.match("dir/"))
        self.assertEqual(False, matcher.match("dir1"))
        self.assertEqual(False, matcher.match("dir/dir2"))
