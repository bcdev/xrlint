from unittest import TestCase

from xrlint.config import Config
from xrlint.plugin import Plugin, PluginMeta
from xrlint.result import get_rules_meta_for_results, Result, Message, Suggestion
from xrlint.rule import RuleOp, RuleMeta


class ResultTest(TestCase):

    # noinspection PyUnusedLocal
    def test_get_rules_meta_for_results(self):

        plugin = Plugin(meta=PluginMeta(name="test"))

        @plugin.define_rule("my-rule-1")
        class MyRule1(RuleOp):
            pass

        @plugin.define_rule("my-rule-2")
        class MyRule2(RuleOp):
            pass

        config = Config(plugins={"test": plugin})
        rules_meta = get_rules_meta_for_results(
            results=[
                Result.new(
                    config,
                    "test.zarr",
                    [Message(message="m 1", rule_id="test/my-rule-1")],
                ),
                Result.new(
                    config,
                    "test.zarr",
                    [Message(message="m 2", rule_id="test/my-rule-2")],
                ),
                Result.new(
                    config,
                    "test.zarr",
                    [Message(message="m 3", rule_id="test/my-rule-1")],
                ),
                Result.new(
                    config,
                    "test.zarr",
                    [Message(message="m 4", rule_id="test/my-rule-2")],
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
        result = Result.new(
            Config(),
            "test.zarr",
            [],
        )
        html = result._repr_html_()
        self.assertIsInstance(html, str)
        self.assertEqual('<p role="file">test.zarr - ok</p>\n', html)

        result = Result.new(
            Config(),
            "test.zarr",
            [Message(message="m 1", rule_id="test/my-rule-1")],
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
