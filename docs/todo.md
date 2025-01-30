# To Do

## Required

- populate `core` plugin by more rules, see CF site and `cf-check` tool
- populate `xcube` plugin by more rules
- enhance docs
  - complete configuration page
  - provide guide page
  - use mkdocstrings ref syntax in docstrings
  - provide configuration examples (use as tests?)
  - add `docs_url` to all existing rules 
- API changes for v0.5:
  - clarify when users can pass configuration objects like values 
    and when configuration like values
  - config class naming is confusing, 
    change `Config` -> `ConfigObject`, `ConfigList` -> `Config`
  - Change `verify` -> `validate`, 
    prefix `RuleOp` methods by `validate_` for clarity.

## Desired
 
- project logo
- apply rule op args/kwargs validation schema 
- provide core rule that checks for configurable list of std attributes
- measure time it takes to open a dataset and pass time into rule context 
  so we can write a configurable rule that checks the opening time
- allow outputting suggestions, if any, that are emitted by some rules
- enhance styling of `Result` representation in Jupyter notebooks
  (check if we can expand/collapse messages with suggestions)

## Nice to have

- add some more tests so we reach 100% coverage
- support `autofix` feature
- support `md` (markdown) output format
- support formatter op args/kwargs and apply validation schema

# Ideas

## Allow for different dataset openers

- introduce `dataset_options` config:
  - `opener: OpenerOp`
  - `opener_options: dict[str, Any]`

## Other plugins

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

