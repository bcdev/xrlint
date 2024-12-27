from unittest import TestCase


expected_api = [
    "AttrNode",
    "AttrsNode",
    "CliEngine",
    "Config",
    "DataArrayNode",
    "DatasetNode",
    "EditInfo",
    "EffectiveConfig",
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
    "Result",
    "Rule",
    "RuleConfig",
    "RuleContext",
    "RuleMeta",
    "RuleOp",
    "RuleRegistry",
    "RuleTest",
    "RuleTester",
    "Suggestion",
    "get_rules_meta_for_results",
    "import_formatters",
    "import_rules",
]


class ApiTest(TestCase):
    def test_api_is_complete(self):
        import xrlint.api as xrl

        # from xrlint import api as xrlint_api

        keys = sorted(
            k
            for k, v in xrl.__dict__.items()
            if isinstance(k, str) and not k.startswith("__")
        )
        self.assertEqual(
            expected_api,
            keys,
        )
