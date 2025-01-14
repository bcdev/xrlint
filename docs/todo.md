# To Do

## Required

- populate `core` plugin by more rules, see CF site and `cf-check` tool
- populate `xcube` plugin by more rules
- add `docs`
  - use mkdocstrings ref syntax in docstrings
  - provide configuration examples (use as tests?)

## Desired
 
- project logo
- support validating xcube 'levels' format. Options:
    - implement xarray backend so we can open them using `xr.open_dataset`
      with `opener_options: {"engine": "xc-levels"}`.
    - implement a `xrlint.processor.Processor` for that purpose.
- add some more tests so we reach 99% coverage
- support rule op args/kwargs schema validation
- Support `RuleTest.expected`, it is currently unused

## Nice to have

- support `autofix` feature
- support `md` (markdown) output format
- support formatter op args/kwargs schema validation

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

