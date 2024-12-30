[![CI](https://github.com/bcdev/xrlint/actions/workflows/tests.yml/badge.svg)](https://github.com/bcdev/xrlint/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/bcdev/xrlint/graph/badge.svg?token=GVKuJao97t)](https://codecov.io/gh/bcdev/xrlint)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![GitHub License](https://img.shields.io/github/license/bcdev/xrlint)](https://github.com/bcdev/xrlint)

# XRLint - A linter for xarray datasets


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

## To-Dos

### Required

- populate `core` plugin by more rules
- populate `xcube` plugin by more rules
- add `docs`
  - configure api docs, use mkdocstrings ref syntax in docstrings
  - generate markdown rule reference for the docs
- CI for package publishing

### Desired
 
- add some more tests so we reach 99% coverage
- introduce `dataset_options` config:
    - `opener: OpenerOp`
    - `opener_options: dict[str, Any]`
- implement `autofix` feature

### Nice to have
 
- use `RuleMeta.type`, it is currently unused
- use `RuleTest.expected`, it is currently unused
- use `processor: ProcessorOp` config, it is currently unused
- add missing community standards, 
  see https://github.com/bcdev/xrlint/community 

## Ideas

### Other plugins

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
   - find opener for file path
   - open data 
2. verify data
   - find root element type and visitor type for data 
   - call the root element `accept(verifier)` that verifies the 
     root element `verify.root()` and starts traversal of 
     child elements.
