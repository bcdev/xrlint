# xrlint - A linter for datasets


xrlint is a [linter](https://en.wikipedia.org/wiki/Lint_(software)) 
tool and library for [xarray]() datasets.

Its design is heavily inspired by [ESLint](https://eslint.org/).


## Rule naming

The rule naming conventions for xrlint are the same as or ESLint:

* Use dashes between words (kebab-case).
* If your rule only disallows something, 
  prefix it with `no-` such as `no-empty-attrs` for disallowing 
  empty attributes in dataset nodes.
* If your rule is enforcing the inclusion of something, 
  use a short name without a special prefix.
* Plugins should add a prefix before their rule names
  separated by a slash, e.g., `cf-conv/dataset-title`.


# TODO

- implement plugin mgt
- add more tests, +coverage
- use `RuleTest.expected`, it is currently unused
- add more rules
- document each rule
- add docs / api docs
- add CI
- generate rule ref

# Ideas

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

## Library design

Exporting stuff from `xrlint`
  - import all api in `xrlint.__init__.py`
  - run `del sys.modules[x]` for all submodules to be hidden
    bit take care of `cli`

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