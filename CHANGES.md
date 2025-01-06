
## Early development snapshots

- Version 0.0.2 (in development) 
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
