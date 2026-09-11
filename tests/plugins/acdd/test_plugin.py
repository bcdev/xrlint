#  Copyright © 2025-2026 Brockmann Consult GmbH and contributors.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from unittest import TestCase

from xrlint.plugins.acdd import export_plugin


class TestACDDPlugin(TestCase):
    def test_rules_complete(self):
        plugin = export_plugin()
        self.assertEqual(
            {
                "1.3-conventions",
                "1.0-attrs-suggested",
                "1.0-attrs-highly-recommended",
                "1.0-attrs-recommended",
                "1.3-attrs-recommended",
                "1.3-attrs-suggested",
                "1.3-attrs-highly-recommended",
                "1.3-no-blanks-in-id",
                "1.3-metadata-link",
                "1.3-dates-iso-format",
            },
            set(plugin.rules.keys()),
        )

    def test_configs_complete(self):
        plugin = export_plugin()
        self.assertEqual(
            {
                "recommended",
                "acdd_1.3",
                "acdd_1.3_strict_recommended",
                "acdd_1.3_strict",
                "acdd_1.3_warn",
                "acdd_1.1",
                "acdd_1.0",
            },
            set(plugin.configs.keys()),
        )
