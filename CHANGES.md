# XRLint Change History

## Version 0.5.0 (in development)

### Adjustments and Enhancements

- Added a new core rule `opening-time` that can be used to check the
  time it takes to open datasets.

- Added HTML styling for both CLI output (`--format html`) and rendering
  of `Result` objects in Jupyter notebooks.

- Rule `no-empty-chunks` has taken off the `"recommended"` settings 
  as there is no easy/efficient way to tell whether a dataset has 
  been written using `write_emtpy_chunks` option or not.
  The rule message itself has been fixed. (#45) 

- Adjusted messages of rules `var-units` and `time-coordinate` 
  to be consistent with messages of other rules.

- Core rule `dataset-title-attr` has been moved into `xcube` plugin
  and renamed to `xcube/dataset-title` because the core rule `var-descr` 
  covers checking for dataset titles.

### Incompatible API changes

- Changed general use of term _verify_ into _validate_: 
  - prefixed `RuleOp` methods by `validate_` for clarity.
  - renamed `XRLint.verify_datasets()` into `validate_files()`
  - renamed `Lint.verify_dataset()` into `validate()`

- Renamed nodes and node properties for clarity and consistency:
  - renamed `DataArrayNode` into `VariableNode`
  - renamed `DataArrayNode.data_array` into `VariableNode.array`

- Various changes for improved clarity regarding configuration management:
  - introduced type aliases `ConfigLike` and `ConfigObjectLike`.
  - renamed `Config` into `ConfigObject` 
  - renamed `ConfigList.configs` into `config_objects` 
  - renamed `ConfigList` into `Config` 
  - renamed `ConfigList.compute_config()` into `compute_config_object()` 
  - renamed `Result.config` into `config_object` 
  - renamed `XRLint.load_config_list()` into `init_config()`
  - added class method `from_config()` to `ConfigList`.
  - removed function `xrlint.config.merge_configs` as it was no longer used.

### Other changes

- XRLint now works with zarr >=2,<3 and zarr >=3.0.2
- Added more tests so we finally reached 100% coverage.
- New `PluginMeta.docs_url` property.

## Version 0.4.1 (from 2025-01-31)

### Changes

- Added core rule `conventions` that checks for the `Conventions`attribute.
- Added core rule `context-descr` that checks content description
- Added core rule `var-descr` that checks data variable description
- Renamed rules for consistency:
  -  `var-units-attrs` and `var-units`  
  -  `flags` into `var-flags`  

### Fixes

- Fixed an issue that prevented recursively traversing folders referred 
  to by URLs (such as `s3://<bucket>/<path>/`) rather than local directory 
  paths. (#39)

## Version 0.4.0 (from 2025-01-27)

- Fixed and enhanced core rule `time-coordinate`. `(#33)
- New xcube rule `no-chunked-coords`. (#29)
- New xcube multi-level dataset rules:
  - `ml-dataset-meta`: verifies that a meta info file exists and is consistent;
  - `ml-dataset-xy`: verifies that the levels have expected spatial resolutions;
  - `ml-dataset-time`: verifies that the levels have expected time dimension, if any.
- Now supporting xcube multi-level datasets `*.levels`:
  - Added xcube plugin processor `"xcube/multi-level-dataset"` that is used
    inside the predefined xcube configurations "all" and "recommended".
- Introduced method `Plugin.define_config` which defines a named plugin
  configuration. It takes a name and a configuration object or list of 
  configuration objects.
- Changed the way how configuration is defined and exported from
  Python configuration files:
  - Renamed function that exports configuration from `export_configs` 
    into `export_config`.
  - The returned value should be a list of values that can be 
    converted into configuration objects: mixed `Config` instances,
    dictionary, or a name that refers to a named configuration of a plugin.

- Other changes:
  - Property `config` of `Linter` now returns a `ConfigList` instead 
    of a `Config` object.  
  - Directories that are recognized by file patterns associated with a non-empty 
    configuration object are no longer recursively traversed.
  - Node path names now contain the dataset index if a file path 
    has been opened by a processor produced multiple 
    datasets to validate.
  - Changed type of `Plugin.configs` from `dict[str, Config]` to 
    `dict[str, list[Config]]`.
  - Inbuilt plugin rules now import their `plugin` instance from
    `xrlint.plugins.<plugin>.plugin` module.
  - `JsonSerializable` now recognizes `dataclass` instances and no longer
    serializes property values that are also default values.
  - Pinned zarr dependency to be >=2.18, <3 until test
    `tests.plugins.xcube.processors.test_mldataset.MultiLevelDatasetProcessorTest`
    is adjusted or `fsspec`'s memory filesystem is updated.
  - Now making use of the `expected` property of `RuleTest`.

## Version 0.3.0 (from 2025-01-20)

- Added more rules
  - core/CF rule "flags"
  - core/CF rule "lon-coordinate"
  - core/CF rule "lat-coordinate"
  - core/CF rule "time-coordinate"  (#15)
  - core rule "no-empty-chunks"
  - xcube rule "time-naming"  (#15)

- Fixed problem where referring to values in modules via 
  the form `"<module>:<attr>"` raised. (#21)

- Introduced factory method `new_plugin` which simplifies
  creating plugin objects.

- Refactored out new common mixin class `Operation`
  which reduces amount of code and simplifies testing
  of operation classes `Rule`, `Processor`, `Formatter`.

- Improved overall test coverage.

- Switched to [ruff](https://docs.astral.sh/ruff/) 
  as default linter and formatter.


## Version 0.2.0 (from 2025-01-14)

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
- Made all docstrings comply to google-style.

## Version 0.1.0 (from 2025-01-09)

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
