#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from unittest import TestCase

from xrlint.plugins.xcube import export_plugin


class ExportPluginTest(TestCase):
    def test_rules_complete(self):
        plugin = export_plugin()
        self.assertEqual(
            {
                "any-spatial-data-var",
                "cube-dims-order",
                "data-var-colors",
                "dataset-title",
                "grid-mapping-naming",
                "increasing-time",
                "lat-lon-naming",
                "ml-dataset-meta",
                "ml-dataset-time",
                "ml-dataset-xy",
                "no-chunked-coords",
                "single-grid-mapping",
                "time-naming",
            },
            set(plugin.rules.keys()),
        )

    def test_configs_complete(self):
        plugin = export_plugin()
        self.assertEqual(
            {
                "all",
                "recommended",
            },
            set(plugin.configs.keys()),
        )
        all_rule_names = set(f"xcube/{k}" for k in plugin.rules.keys())
        self.assertEqual(
            all_rule_names,
            set(plugin.configs["all"][-1].rules.keys()),
        )
        self.assertEqual(
            all_rule_names,
            set(plugin.configs["recommended"][-1].rules.keys()),
        )
