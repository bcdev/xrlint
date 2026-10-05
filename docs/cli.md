# Command Line Interface

After installation, use `xrlint` from a terminal:

```text
xrlint [OPTIONS] [FILES]...
```

`FILES` accepts dataset paths, directories, and remote URLs. The CLI finds
configuration, selects matching datasets, validates each one, and writes a
report. Run `xrlint --help` for the installed version's usage text.

## Common commands

```bash
xrlint --init
xrlint example.nc
xrlint data/
xrlint --config configs/production.yaml data/
xrlint --print-config data/example.nc
xrlint --rule "var-units: error" data/
xrlint --format html --output-file report.html data/
xrlint --format json --output-file report.json --max-warnings 0 data/
```

For a one-off check without a configuration file:

```bash
xrlint --no-config-lookup --rule "no-empty-attrs: warn" example.nc
```

## Options

| Option | Behavior |
| --- | --- |
| `--no-config-lookup` | Disable automatic configuration-file discovery. |
| `-c, --config FILE` | Read this configuration file instead of searching. |
| `--print-config FILE` | Print the computed configuration as JSON and exit, without opening the dataset. |
| `--plugin MODULE` | Load a module exporting `export_plugin()`. Repeat to load multiple plugins. |
| `--rule SPEC` | Append a YAML rule mapping, such as `"var-units: error"`. Repeat for multiple rules; include the space after `:`. |
| `-o, --output-file FILE` | Write the report to a file rather than standard output. |
| `-f, --format NAME` | Select `simple` (default), `json`, or `html`. |
| `--color / --no-color` | Enable or disable styling for simple console output; enabled by default. |
| `--max-warnings COUNT` | Allow this many warnings before failure; default `5`. |
| `--init` | Create `xrlint-config.yaml` in the current directory and exit; refuse to overwrite it. |
| `--version` | Show the installed version and exit. |
| `--help` | Show command help and exit. |

## Configuration and file selection

Without `--config` or `--no-config-lookup`, discovery checks the current directory.
See [Configuration File](config.md#configuration-file) for the exact filename
order, including legacy names. The CLI does not enable a preset automatically
when no file is found; it reports `no rules configured` unless rules are supplied
another way.

By default, dataset discovery selects `**/*.nc` and `**/*.zarr`. Unmatched
directories are walked recursively. A matched dataset directory such as a Zarr
store is processed as a single dataset. Configuration can add file types and
global exclusions; see [File and Ignore Patterns](config.md#file-and-ignore-patterns).

Pass concrete paths or directories. A wildcard argument is expanded only if
your shell expands it; XRLint does not expand it itself. Use `xrlint .` to scan
the current directory. Running `xrlint` with no file arguments does no work.

Remote access requires the appropriate filesystem and dataset backends.
For example, S3 Zarr access requires `s3fs` and `zarr`.
Opening options are configured per dataset; they are not forwarded to the
filesystem used for directory listing. See [Remote datasets](examples.md#remote-datasets).

## Reports

- `simple` streams readable messages with file paths, node paths, rule identifiers,
  and a summary. Reports written to a file are unstyled.
- `json` writes an object with a `results` array. Each result contains a file path
  and serialized messages, and may include its computed configuration.
- `html` writes a browser-readable report.

Messages use severity `1` for warnings and `2` for errors. Fatal messages indicate
problems such as opening failures. A successful write of a report does not mean
validation passed: check the exit status as well.

Use `--output-file` for machine-readable reports. Configuration notices and
warning-limit messages can also appear on standard output.

## Exit status

| Status | Meaning |
| --- | --- |
| `0` | No errors and warnings do not exceed the limit; also successful help, version, initialization, or configuration inspection. |
| `1` | Validation errors, warnings above the limit, or operational errors such as missing configuration or an unknown output format. |
| `2` | Command-line usage errors, such as an unknown option or invalid integer argument. |

With `--max-warnings 5`, five warnings pass and six fail. Use
`--max-warnings 0` to fail on any warning. Negative values do not disable this
check: the implementation compares the count directly with the supplied limit.

A run that selects no datasets can exit successfully, and a bare `xrlint`
invocation also exits successfully without validation. In automation, provide
explicit input paths and verify that your file-selection patterns match data.
