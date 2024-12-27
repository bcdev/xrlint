from unittest import TestCase

from xrlint.util.importutil import import_submodules


class ImportSubmodulesTest(TestCase):
    def test_import_submodules(self):
        modules = import_submodules("tests.util.test_importutil_pkg", dry_run=True)
        self.assertEqual(
            {
                "tests.util.test_importutil_pkg.module1",
                "tests.util.test_importutil_pkg.module2",
            },
            set(modules),
        )

        modules = import_submodules("tests.util.test_importutil_pkg")
        self.assertEqual(
            {
                "tests.util.test_importutil_pkg.module1",
                "tests.util.test_importutil_pkg.module2",
            },
            set(modules),
        )
