from unittest import TestCase

from xrlint.plugin import Plugin
from xrlint.util.importutil import import_submodules
from xrlint.util.importutil import import_value


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

    def test_import_exported_value(self):
        core_plugin = import_value(
            "xrlint.plugins.core", "export_plugin", Plugin.from_value
        )
        self.assertIsInstance(core_plugin, Plugin)
