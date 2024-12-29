from unittest import TestCase

from xrlint.constants import CORE_PLUGIN_NAME

expected_api = [
    "AttrNode",
    "AttrsNode",
    "CliEngine",
    "Config",
    "ConfigList",
    "DataArrayNode",
    "DatasetNode",
    "EditInfo",
    "Formatter",
    "FormatterContext",
    "FormatterMeta",
    "FormatterOp",
    "FormatterRegistry",
    "Linter",
    "Message",
    "Node",
    "Plugin",
    "PluginMeta",
    "Processor",
    "ProcessorMeta",
    "ProcessorOp",
    "Result",
    "Rule",
    "RuleConfig",
    "RuleContext",
    "RuleMeta",
    "RuleOp",
    "RuleTest",
    "RuleTester",
    "Suggestion",
    "core_plugin",
    "formatters",
    "get_rules_meta_for_results",
    "new_linter",
    "version",
    "xcube_plugin",
]


class AllTest(TestCase):
    def test_api_is_complete(self):
        import xrlint.all as xrl

        keys = sorted(
            k
            for k, v in xrl.__dict__.items()
            if isinstance(k, str) and not k.startswith("_")
        )
        self.assertEqual(
            expected_api,
            keys,
        )

    def test_new_linter(self):
        import xrlint.all as xrl

        linter = xrl.new_linter()
        self.assertIsInstance(linter, xrl.Linter)
        self.assertIsInstance(linter.config.plugins, dict)
        self.assertEqual({CORE_PLUGIN_NAME, "xcube"}, set(linter.config.plugins.keys()))
        self.assertIsInstance(linter.config.rules, dict)
        self.assertIn("dataset-title-attr", linter.config.rules)
        self.assertIn("xcube/spatial-dims-order", linter.config.rules)

        linter = xrl.new_linter(recommended=False)
        self.assertIsInstance(linter, xrl.Linter)
        self.assertIsInstance(linter.config.plugins, dict)
        self.assertEqual({CORE_PLUGIN_NAME, "xcube"}, set(linter.config.plugins.keys()))
        self.assertEqual(None, linter.config.rules)
