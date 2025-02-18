# Python API

This chapter provides a plain reference for the XRLint Python API.

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
  base classes [None][xrlint.node.Node], [XarrayNode][xrlint.node.XarrayNode],
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
  the `xrlint.all` convenience module exports all of the above from a 
  single module.
  
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

## Testing API

::: xrlint.testing.RuleTester

::: xrlint.testing.RuleTest

