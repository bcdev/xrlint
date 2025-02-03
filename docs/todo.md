# To Do

## Required

- support zarr >= 3 which we do not only because test 
  `tests/plugins/xcube/processors/test_mldataset.py` fails
  (see code TODO)
- enhance docs
  - complete configuration page
  - provide guide page
  - use mkdocstrings ref syntax in docstrings
  - provide configuration examples (use as tests?)
  - add `docs_url` to all existing rules 
  - rule ref should cover rule parameters

## Desired
 
- project logo
- add `xcube` rule that helps to identify chunking issues 
- apply rule op args/kwargs validation schema 
- allow outputting suggestions, if any, that are emitted by some rules
  - add CLI option
  - expand/collapse messages with suggestions in Jupyter notebooks
- validate `RuleConfig.args/kwargs` against `RuleMeta.schema`
  (see code TODO)

## Nice to have

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

Do not limit validations to `xr.Dataset`.
However, this requires new rule sets.

To allow for other data models, we need to allow 
for a specific validator type for a given data type.

The validator validates specific node types
that are characteristic for a data type.

To do so a traverser must traverse the elements of the data
and pass each node to the validator.

Note, this is the [_Visitor Pattern_](https://en.wikipedia.org/wiki/Visitor_pattern), 
where the validator is the _Visitor_ and a node refers to _Element_.

To support the CLI mode, we need different data opener 
types that can read the data from a file path.

1. open data, if given data is a file path: 
   - find opener for file path
   - open data 
2. validate data
   - find root element type and visitor type for data 
   - call the root element `accept(validator)` that validates the 
     root element `validate.root()` and starts traversal of 
     child elements.
