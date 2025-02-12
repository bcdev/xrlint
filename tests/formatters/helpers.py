#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from xrlint.config import ConfigObject
from xrlint.formatter import FormatterContext
from xrlint.plugin import new_plugin
from xrlint.result import Message, Result, ResultStats
from xrlint.rule import RuleOp


class FormatterContextImpl(FormatterContext):
    def __init__(self, max_warnings: int = -1):
        self._max_warnings = max_warnings
        self._result_stats = ResultStats()

    @property
    def max_warnings_exceeded(self) -> bool:
        return self._result_stats.warning_count > self._max_warnings

    @property
    def result_stats(self) -> ResultStats:
        return self._result_stats


def get_context(max_warnings: int = -1) -> FormatterContext:
    return FormatterContextImpl(max_warnings)


def get_test_results():
    plugin = new_plugin(name="test")

    @plugin.define_rule(
        "rule-1", description="Haha", docs_url="https://rules.com/haha.html"
    )
    class Rule1(RuleOp):
        pass

    @plugin.define_rule(
        "rule-2", description="Hoho", docs_url="https://rules.com/hoho.html"
    )
    class Rule2(RuleOp):
        pass

    config_obj = ConfigObject(plugins={"test": plugin})

    return [
        Result(
            file_path="test.nc",
            config_object=config_obj,
            messages=[
                Message(
                    message="message-1",
                    rule_id="test/rule-1",
                    severity=2,
                    node_path="dataset",
                ),
                Message(
                    message="message-2",
                    rule_id="test/rule-2",
                    severity=1,
                    node_path="dataset",
                ),
                Message(message="message-3", fatal=True),
            ],
        ),
        Result(
            file_path="test.nc",
            config_object=config_obj,
            messages=[
                Message(message="message-1", rule_id="test/rule-1", severity=1),
                Message(message="message-2", rule_id="test/rule-2", severity=2),
                Message(message="message-3", fatal=False),
            ],
        ),
    ]
