# Python API

Use `new_linter()` for individual datasets and `XRLint` for file discovery and
reports. The reference below is generated from the public classes and functions.

## Validate a dataset

```python
import xarray as xr
from xrlint.linter import new_linter

linter = new_linter("recommended", rules={"var-units": "error"})
dataset = xr.Dataset(attrs={"title": "Example dataset"})
result = linter.validate(dataset, file_path="example.nc")

for message in result.messages:
    print(message.severity, message.rule_id, message.node_path, message.message)

assert result.fatal_error_count == 0
```

`new_linter()` loads installed plugins, but enables only the rules you configure.
It does not read configuration files. `Linter()` alone starts without plugin
registrations. Both accept configuration objects and named presets; additional
configuration passed to `validate()` is merged after the linter's configuration.

Pass a source path to open a dataset, for example `linter.validate("example.nc")`.
The default opener closes files it opens. Existing datasets remain under the
caller's control. `file_path` labels in-memory results and also determines which
file-specific configuration objects match.

Findings are returned in `Result.messages`. Severity `1` means warning and `2`
means error. Inspect `error_count`, `warning_count`, and `fatal_error_count`, and
use `message.suggestions` for any suggested corrections. Configuration or custom
rule errors may raise exceptions; not every failure is converted to a result.

`result.to_json()` returns Python JSON-compatible values; use `json.dumps()` to
encode them. `result.to_html()` returns HTML, and notebooks display the result
as HTML automatically. This API does not apply the CLI's warning threshold.

## Validate files and write reports

```python
from xrlint.cli.engine import XRLint

engine = XRLint(
    no_config_lookup=True,
    output_format="json",
    output_path="report.json",
    max_warnings=0,
)
engine.init_config("recommended")
results = engine.validate_files(["data/"])
report = engine.format_results(results)
engine.write_report(report)

failed = engine.result_stats.error_count > 0 or engine.max_warnings_exceeded
print(f"Checked {engine.result_stats.result_count} datasets; failed={failed}")
```

`validate_files()` returns an iterator: validation happens as you consume it.
`format_results()` consumes it and updates `result_stats`. Statistics accumulate
on the engine, so create a new engine for an independent run. Engine methods do
not terminate your process; inspect the counts to implement your own exit policy.

To read a specific configuration, construct `XRLint(config_path="config.yaml")`
and call `init_config()`. With default constructor options, `init_config()` uses
the same working-directory discovery as the CLI. Arguments to `init_config()`
are appended after file and command-line rule configuration.

## Dataset trees

Pass an `xr.DataTree` directly to `validate()` to validate grouped data. Tree
traversal visits group nodes and the datasets at leaves. A tree without children
is treated as a dataset. Dataset contents on non-leaf groups are not independently
traversed. The core `conventions` and `content-desc` rules consider inherited
parent-group attributes, with local attributes taking precedence.

Import tree-specific node types directly:

```python
from xrlint.node import DataTreeNode, XarrayNode
```

These types are not currently re-exported by `xrlint.all`.

## Overview

- The top-level API component is the class [XRLint][xrlint.cli.engine.XRLint]
  which encapsulates the functionality of the [XRLint CLI](cli.md).
- The `linter` module provides the functionality for linting a single 
  dataset:
  [new_linter()][xrlint.linter.new_linter] factory function and the
  [Linter][xrlint.linter.Linter] class.
- The `plugin` module provides plugin related components:
  A factory [new_plugin][xrlint.plugin.new_plugin] to create instances of
  the [Plugin][xrlint.plugin.Plugin] class that comprises 
  plugin metadata represented by [PluginMeta][xrlint.plugin.PluginMeta].
- The `config` module provides classes that represent 
  configuration information and provide related functionality:
  [Config][xrlint.config.Config] and [ConfigObject][xrlint.config.ConfigObject].
- The `rule` module provides rule related classes and functions:
  [Rule][xrlint.rule.Rule] comprising rule metadata, 
  [RuleMeta][xrlint.rule.RuleMeta], the rule validation operations in 
  [RuleOp][xrlint.rule.RuleOp], as well as related to the latter
  [RuleContext][xrlint.rule.RuleContext] and [RuleExit][xrlint.rule.RuleExit].
  Decorator [define_rule][xrlint.rule.define_rule] allows defining rules.
- The `node` module defines the nodes passed to [RuleOp][xrlint.rule.RuleOp]:
  base classes [Node][xrlint.node.Node], [XarrayNode][xrlint.node.XarrayNode],
  and the specific nodes [DataTreeNode][xrlint.node.DataTreeNode], 
  [DatasetNode][xrlint.node.DatasetNode], [VariableNode][xrlint.node.VariableNode], 
  [AttrsNode][xrlint.node.AttrsNode], and [AttrNode][xrlint.node.AttrNode].
- The `processor` module provides processor related classes and functions:
  [Processor][xrlint.processor.Processor] comprising processor metadata
  [ProcessorMeta][xrlint.processor.ProcessorMeta], 
  and the processor operation [ProcessorOp][xrlint.processor.ProcessorOp].
  Decorator [define_processor][xrlint.processor.define_processor] allows defining 
  processors.
- The `result` module provides data classes that are used to 
  represent validation results:
  [Result][xrlint.result.Result] composed of [Messages][xrlint.result.Message],
  which again may contain [Suggestions][xrlint.result.Suggestion].
- Finally, the `testing` module provides classes for rule testing:
  [RuleTester][xrlint.testing.RuleTester] that is made up 
  of [RuleTest][xrlint.testing.RuleTest]s.

Note: 
  the `xrlint.all` convenience module exports many common API definitions from
  one module. Use the direct imports in this reference for definitions it does
  not export, including `DataTreeNode`, `XarrayNode`, and `ResultStats`.
  
## CLI API

::: xrlint.cli.engine.XRLint

## Linter API

::: xrlint.linter.new_linter

::: xrlint.linter.Linter

## Plugin API

::: xrlint.plugin.new_plugin

::: xrlint.plugin.Plugin

::: xrlint.plugin.PluginMeta

## Configuration API

::: xrlint.config.Config

::: xrlint.config.ConfigObject

::: xrlint.config.ConfigLike

::: xrlint.config.ConfigObjectLike

## Rule API

::: xrlint.rule.define_rule

::: xrlint.rule.Rule

::: xrlint.rule.RuleMeta

::: xrlint.rule.RuleConfig
    options:
      inherited_members:
        - from_value

::: xrlint.rule.RuleOp

::: xrlint.rule.RuleContext

::: xrlint.rule.RuleExit

## Dataset Node API

::: xrlint.node.Node

::: xrlint.node.XarrayNode

::: xrlint.node.DataTreeNode

::: xrlint.node.DatasetNode

::: xrlint.node.VariableNode

::: xrlint.node.AttrsNode

::: xrlint.node.AttrNode

## Processor API

::: xrlint.processor.define_processor

::: xrlint.processor.Processor

::: xrlint.processor.ProcessorMeta
 
::: xrlint.processor.ProcessorOp

## Result API

::: xrlint.result.Result

::: xrlint.result.Message

::: xrlint.result.Suggestion

::: xrlint.result.ResultStats

## Formatter API

The CLI provides `simple`, `json`, and `html` formatters. The formatter interfaces
are also available to applications that need to build their own reports.

::: xrlint.formatter.Formatter

::: xrlint.formatter.FormatterMeta

::: xrlint.formatter.FormatterOp

::: xrlint.formatter.FormatterContext

::: xrlint.formatter.FormatterRegistry

## Testing API

::: xrlint.testing.RuleTester

::: xrlint.testing.RuleTest

