# XRLint - A linter for datasets


XRLint is a [linter](https://en.wikipedia.org/wiki/Lint_(software)) 
tool and library for [xarray]() datasets.

Its design is heavily inspired by [ESLint](https://eslint.org/).

## Inbuilt Rules

- `core`: Implementing the rules for
  [tiny data](https://tutorial.xarray.dev/intermediate/data_cleaning/05.1_intro.html)
  and the 
  [CF-Conventions](https://cfconventions.org/cf-conventions/cf-conventions.html)

- `xcube`: Implementing the rules for 
  [xcube datasets](https://xcube.readthedocs.io/en/latest/cubespec.html)

## Contributing Rules

### Rule Naming

The rule naming conventions for XRLint are the same as or ESLint:

* Lower-case only.
* Use dashes between words (kebab-case).
* If your rule only disallows something, 
  prefix it with `no-` such as `no-empty-attrs` for disallowing 
  empty attributes in dataset nodes.
* If your rule is enforcing the inclusion of something, 
  use a short name without a special prefix.
* Plugins should add a prefix before their rule names
  separated by a slash, e.g., `xcube/spatial-dims-order`.

### Rule Design

* The reasoning behind a rule should be **easy to grasp**. 

* A rule should serve for a **single purpose only**. Try subdividing
  complex rule logic into multiple rules with simpler logic.

* Each rule should be defined in a dedicated module named after the rule, 
  i.e., `<plugin>/rules/<rule>`. The module name should be the rule's name
  with dashes replaced by underscores. 

* Write a comprehensive test for your rule logic using 
  `xrlint.testing.RuleTester`. It should be defined in a dedicated 
  test module, i.e., `tests/rules/test_<rule>`.

# TODO

- introduce `dataset_options` config:
-   `opener: OpenerOp`
-   `opener_options: dict[str, Any]`
- add more tests, +coverage
- use `RuleMeta.type`, it is currently unused
- use `RuleTest.expected`, it is currently unused
- use `processor: ProcessorOp` config, it is currently unused
- add docs / api docs
- add CI
- generate rule ref
- populate `core` plugin
- populate `xcube` plugin
- autofixing feature

# Ideas

## Plugins

- `sgrid`: https://sgrid.github.io/sgrid/
- `ugrid`: https://ugrid-conventions.github.io/ugrid-conventions/

## Generalize data linting

Do not limit verification to `xr.Dataset`.
However, this requires new rule sets.

To allow for other data models, we need to allow 
for a specific verifier type for a given data type.

The verifier verifies specific node types
that are characteristic for a data type.

To do so a traverser must traverse the elements of the data
and pass each node to the verifier.

Note, this is the [_Visitor Pattern_](https://en.wikipedia.org/wiki/Visitor_pattern), 
where the verifier is the _Visitor_ and a node refers to _Element_.

To support the CLI mode, we need different data opener 
types that can read the data from a file path.

1. open data, if given data is a file path: 
   a. find opener for file path
   b. open data 
2. verify data
   a. find root element type and visitor type for data 
   b. call the root element `accept(verifier)` that verifies the 
      root element `verify.root()` and starts traversal of 
      child elements.


## Config design

- config
  - plugins[str, plugin] 
  - rules[str, rule_config]
  - settings[str, any]
  - ...
  - files
  - ignores

- plugin
  - meta
  - rules[str, rule]
  - processors