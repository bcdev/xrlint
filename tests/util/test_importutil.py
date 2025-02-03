#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from unittest import TestCase

import pytest

from xrlint.plugin import Plugin
from xrlint.util.importutil import ValueImportError, import_submodules, import_value


def get_foo():
    return 42


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


class ImportValueTest(TestCase):
    def test_import_exported_value_ok(self):
        plugin, plugin_ref = import_value(
            "xrlint.plugins.core", "export_plugin", factory=Plugin.from_value
        )
        self.assertIsInstance(plugin, Plugin)
        self.assertEqual("xrlint.plugins.core:export_plugin", plugin_ref)

    def test_import_exported_value_ok_no_factory(self):
        value, value_ref = import_value(
            "tests.util.test_importutil:get_foo",
        )
        self.assertEqual(value, 42)
        self.assertEqual("tests.util.test_importutil:get_foo", value_ref)

    # noinspection PyMethodMayBeStatic
    def test_import_exported_value_fail(self):
        with pytest.raises(
            ValueImportError,
            match=(
                r"value of tests.util.test_importutil:get_foo\(\)"
                r" must be of type float, but got int"
            ),
        ):
            import_value("tests.util.test_importutil:get_foo", expected_type=float)

    # noinspection PyMethodMayBeStatic
    def test_import_exported_value_import_error(self):
        with pytest.raises(
            ValueImportError,
            match=(
                "failed to import value from 'tests.util.test_baz:get_foo':"
                " No module named 'tests.util.test_baz'"
            ),
        ):
            import_value("tests.util.test_baz:get_foo")
