# XRLint Change History

## Version 0.2.0 (14.01.2025)

- Rule description is now your `RuleOp`'s docstring
  if `description` is not explicitly provided.
- Supporting _virtual plugins_: plugins provided by Python 
  dictionaries with rules defined by the `RuleOp` classes.
- Added more configuration examples in the `examples` folder.
- All `xcube` rules now have references into the 
  xcube dataset specification.
- Introduced mixin classes `ValueConstructible` and 
  derived `MappingConstructible` which greatly simplify
  flexible instantiation of XRLint's configuration objects 
  and their children from Python and JSON/YAML values.
- Make all docstrings comply to google-style.

## Version 0.1.0 (09.01.2025)

- Added CLI option `--print-config PATH`, see same option in ESLint
- XRLint CLI now outputs single results immediately to console,
  instead only after all results have been collected.
- Refactored and renamed `CliEngine` into `XRLint`. Documented the class.
- `new_linter()` now uses a config name arg instead of a bool arg.
- Split example notebook into two


## Early development snapshots

- Version 0.0.3 (08.01.2025)
  - enhanced "simple" output format by colors and links 
  - new xcube rule "increasing-time"
  - new xcube rule "data-var-colors"
  - new `RuleExit` exception to exit rule logic and 
    stop further node traversal

- Version 0.0.2 (06.01.2025) 
  - more rules
  - more tests
  - config list item can be config name
  - xcube is no longer default plugin
  - no rules by default
  - no rules configured is an error
  - CLI exit code 1 with max warnings exceeded 
  - CLI exit code 1 with no files given
  - new CLI options `--plugin`, `--rule`, `--init`
  - markdown rule reference in docs via `mkruleref.py` tool
  - using `files` config option to specify valid filename extensions, see
    [here](https://eslint.org/docs/latest/use/configure/configuration-files#specifying-files-with-arbitrary-extensions)
  - using default filename extensions `["**/*.zarr", "**/*.nc"]`
  - using subset of [minimatch](https://github.com/isaacs/minimatch) 
    syntax instead of the simple globs used by Python's `fnmatch`
  - allow the CLI's `FILES` args to contain directories, which are 
    automatically recursively traversed
  - rule `coords-for-dims` works on dataset level
  - support for custom processors
  
- Version 0.0.1 (30.12.2024) - Initial version. 
