#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from unittest import TestCase

import xarray as xr

# noinspection PyProtectedMember
from xrlint._linter.rulectx import RuleContextImpl
from xrlint.config import ConfigObject
from xrlint.constants import DATASET_ROOT_NAME
from xrlint.result import Message, Suggestion


class RuleContextImplTest(TestCase):
    def test_defaults(self):
        config_obj = ConfigObject()
        dataset = xr.Dataset()
        context = RuleContextImpl(config_obj, dataset, "./ds.zarr", None, None)
        self.assertIs(config_obj, context.config)
        self.assertIs(dataset, context.dataset)
        self.assertEqual({}, context.settings)
        self.assertEqual("./ds.zarr", context.file_path)
        self.assertEqual(None, context.file_index)
        self.assertEqual(None, context.access_latency)

    def test_report(self):
        context = RuleContextImpl(
            ConfigObject(), xr.Dataset(), "./ds.zarr", None, 1.2345
        )
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
                    node_path=DATASET_ROOT_NAME,
                    rule_id="no-xxx",
                    severity=2,
                    suggestions=[
                        Suggestion(desc="Never say XXX again.", data=None, fix=None)
                    ],
                ),
                Message(
                    message="You said it.",
                    node_path=DATASET_ROOT_NAME,
                    rule_id="no-xxx",
                    severity=2,
                    fatal=True,
                    suggestions=None,
                ),
            ],
            context.messages,
        )
