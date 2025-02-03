"""
This configuration example demonstrates how to
define and use "virtual" plugins. Such plugins
can be defined inside a configuration item.
"""

#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from xrlint.node import DatasetNode
from xrlint.rule import RuleContext, RuleOp, define_rule


@define_rule("good-title", description="Dataset title should be 'Hello World!'.")
class GoodTitle(RuleOp):
    def validate_dataset(self, ctx: RuleContext, node: DatasetNode):
        good_title = "Hello World!"
        if node.dataset.attrs.get("title") != good_title:
            ctx.report(
                "Attribute 'title' wrong.",
                suggestions=[f"Rename it to {good_title!r}."],
            )


# Define more rules here...


def export_config():
    return [
        # Define and use "hello" plugin
        {
            "plugins": {
                "hello": {
                    "meta": {
                        "name": "hello",
                        "version": "1.0.0",
                    },
                    "rules": {
                        "good-title": GoodTitle,
                        # Add more rules here...
                    },
                    "configs": {
                        "recommended": [
                            {
                                "rules": {
                                    "hello/good-title": "warn",
                                    # Configure more rules here...
                                },
                            }
                        ],
                        # Add more configurations here...
                    },
                },
            }
        },
        # Use recommended settings from xrlint
        "recommended",
        # Use recommended settings from "hello" plugin
        "hello/recommended",
    ]
