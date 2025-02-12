#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from unittest import TestCase

from xrlint.config import ConfigObject
from xrlint.plugin import new_plugin
from xrlint.result import (
    Message,
    Result,
    ResultStats,
    Suggestion,
    get_rules_meta_for_results,
)
from xrlint.rule import RuleMeta, RuleOp


class ResultTest(TestCase):
    # noinspection PyUnusedLocal
    def test_get_rules_meta_for_results(self):
        plugin = new_plugin(name="test")

        @plugin.define_rule("my-rule-1")
        class MyRule1(RuleOp):
            pass

        @plugin.define_rule("my-rule-2")
        class MyRule2(RuleOp):
            pass

        config_obj = ConfigObject(plugins={"test": plugin})
        rules_meta = get_rules_meta_for_results(
            results=[
                Result(
                    file_path="test.zarr",
                    config_object=config_obj,
                    messages=[Message(message="m 1", rule_id="test/my-rule-1")],
                ),
                Result(
                    file_path="test.zarr",
                    config_object=config_obj,
                    messages=[Message(message="m 2", rule_id="test/my-rule-2")],
                ),
                Result(
                    file_path="test.zarr",
                    config_object=config_obj,
                    messages=[Message(message="m 3", rule_id="test/my-rule-1")],
                ),
                Result(
                    file_path="test.zarr",
                    config_object=config_obj,
                    messages=[Message(message="m 4", rule_id="test/my-rule-2")],
                ),
            ]
        )

        self.assertIsInstance(rules_meta, dict)
        self.assertEqual(2, len(rules_meta))
        for k, v in rules_meta.items():
            self.assertIsInstance(k, str)
            self.assertIsInstance(v, RuleMeta)
        self.assertEqual(
            {"test/my-rule-1", "test/my-rule-2"},
            set(rules_meta.keys()),
        )

    def test_repr_html(self):
        result = Result(
            file_path="test.zarr",
            config_object=ConfigObject(),
            messages=[],
        )
        html = result._repr_html_()
        self.assertIsInstance(html, str)
        self.assertIn("ok", html)
        self.assertIn("<div", html)

        result = Result(
            file_path="test.zarr",
            config_object=ConfigObject(),
            messages=[Message(message="m 1", rule_id="test/my-rule-1")],
        )
        html = result._repr_html_()
        self.assertIsInstance(html, str)
        self.assertIn("<table>", html)
        self.assertIn("</table>", html)


class SuggestionTest(TestCase):
    # noinspection PyUnusedLocal
    def test_from_value(self):
        self.assertEqual(
            Suggestion("Use xr.transpose()"),
            Suggestion.from_value("Use xr.transpose()"),
        )

        suggestion = Suggestion("Use xr.transpose()")
        self.assertIs(suggestion, Suggestion.from_value(suggestion))


class ResultStatsTest(TestCase):
    def test_collect(self):
        stats = ResultStats()

        self.assertEqual(0, stats.error_count)
        self.assertEqual(0, stats.warning_count)
        self.assertEqual(0, stats.result_count)

        results = [
            Result(
                file_path="test.zarr",
                messages=[
                    Message("R1 M1", severity=1),
                    Message("R1 M2", severity=2),
                ],
            ),
            Result(
                file_path="test.zarr",
                messages=[
                    Message("R2 M1", severity=2),
                ],
            ),
            Result(
                file_path="test.zarr",
                messages=[
                    Message("R3 M1", severity=1),
                    Message("R3 M2", severity=2),
                    Message("R3 M3", severity=2),
                ],
            ),
        ]

        results2 = list(stats.collect(results))

        self.assertEqual(results, results2)
        self.assertEqual(4, stats.error_count)
        self.assertEqual(2, stats.warning_count)
        self.assertEqual(3, stats.result_count)
