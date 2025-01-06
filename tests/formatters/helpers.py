from xrlint.config import Config
from xrlint.plugin import Plugin
from xrlint.plugin import PluginMeta
from xrlint.result import Message
from xrlint.result import Result
from xrlint.rule import RuleOp


def get_test_results():

    plugin = Plugin(meta=PluginMeta(name="test"))

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

    config = Config(plugins={"test": plugin})

    return [
        Result.new(
            config,
            file_path="test.nc",
            messages=[
                Message(message="message-1", rule_id="test/rule-1", severity=2),
                Message(message="message-2", rule_id="test/rule-2", severity=1),
                Message(message="message-3", fatal=True),
            ],
        ),
        Result.new(
            config,
            file_path="test-2.nc",
            messages=[
                Message(message="message-1", rule_id="test/rule-1", severity=1),
                Message(message="message-2", rule_id="test/rule-2", severity=2),
                Message(message="message-3", fatal=False),
            ],
        ),
    ]
