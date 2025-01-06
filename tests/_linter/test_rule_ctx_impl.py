from unittest import TestCase

import xarray as xr

# noinspection PyProtectedMember
from xrlint._linter.rulectx import RuleContextImpl
from xrlint.config import Config
from xrlint.result import Suggestion, Message


class RuleContextImplTest(TestCase):
    def test_defaults(self):
        config = Config()
        dataset = xr.Dataset()
        context = RuleContextImpl(config, dataset, "./ds.zarr")
        self.assertIs(config, context.config)
        self.assertIs(dataset, context.dataset)
        self.assertEqual({}, context.settings)
        self.assertEqual("./ds.zarr", context.file_path)

    def test_report(self):
        context = RuleContextImpl(Config(), xr.Dataset(), "./ds.zarr")
        with context.use_state(rule_id="no-xxx"):
            context.report(
                "What the heck do you mean?",
                suggestions=[Suggestion("Never say XXX again.")],
            )
            context.report("You said it.", fatal=True)
        self.assertEqual(
            [
                Message(
                    message="What the heck do you mean?",
                    rule_id="no-xxx",
                    severity=2,
                    suggestions=[
                        Suggestion(desc="Never say XXX again.", data=None, fix=None)
                    ],
                ),
                Message(
                    message="You said it.",
                    rule_id="no-xxx",
                    severity=2,
                    fatal=True,
                    suggestions=None,
                ),
            ],
            context.messages,
        )
