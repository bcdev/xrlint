# Getting Started

## Installation

XRLint requires Python 3.10 or newer:

```bash
python -m pip install xrlint
```

Alternatively, install with conda:

```bash
conda install -c conda-forge xrlint
```

Install a backend for the files you want to open. For the NetCDF example below:

```bash
python -m pip install netCDF4
```

For Zarr files, install `zarr`; for S3 access, install `s3fs` as well.
The base package does not install every storage backend.

## Command line interface

Run the following commands in a new working directory:

```bash
xrlint --help
xrlint --init
```

Initialization creates `xrlint-config.yaml`:

```yaml
- recommended
```

This enables the core recommended rules. `--init` refuses to overwrite an
existing file. XRLint discovers configuration in the current working directory,
not next to each dataset.

Save this Python script as `make_example.py` and run it with
`python make_example.py`:

```python
import xarray as xr

dataset = xr.Dataset(attrs={"title": "Example dataset"})
dataset.to_netcdf("example.nc", engine="netcdf4")
```

Validate the file:

```bash
xrlint example.nc
```

This minimal dataset is intentionally missing some metadata, so warnings are
expected. Reports identify the rule and the affected dataset node.
The CLI exits with status 1 for any error or when warnings exceed the default
limit of five. To fail on any warning, use `--max-warnings 0`.

Add overrides after the preset in `xrlint-config.yaml`:

```yaml
- recommended
- rules:
    no-empty-attrs: "off"
    var-units: warn
    grid-mappings: error
```

Check an entire directory, inspect configuration, or write a report:

```bash
xrlint data/
xrlint --print-config example.nc
xrlint --format json --output-file report.json example.nc
```

Pass a directory explicitly to scan it; running `xrlint` without file arguments
does not scan the current directory. See [CLI](cli.md) for all options and exit
behavior.

## Add plugin rules

The installed `core`, `xcube`, and `acdd` plugins are discovered automatically.
Add a preset to enable its checks:

```yaml
- recommended
- xcube/recommended
- rules:
    xcube/grid-mapping-naming: "off"
    xcube/lat-lon-naming: warn
```

Use `acdd/recommended` for ACDD 1.3 metadata checks. Plugin presets do not
implicitly enable core rules, so keep `recommended` when you want both.
See [Configuration](config.md) for all presets and custom plugin registration.

## Python API

Use `new_linter()` to load installed plugins and select rules explicitly:

```python
import xarray as xr
from xrlint.linter import new_linter

dataset = xr.Dataset(attrs={"title": "Example dataset"})
linter = new_linter("recommended")
result = linter.validate(dataset, file_path="example.nc")

print(f"{result.error_count} errors, {result.warning_count} warnings")
for message in result.messages:
    print(message.rule_id, message.node_path, message.message)
```

`file_path` labels the result and controls file-specific configuration matching;
it does not open a file when the input is already an xarray object.
To open a file, call `linter.validate("example.nc")`.

In a notebook, display `result` as the last expression in a cell for an HTML
report. Many public classes are also available through `import xrlint.all as xrl`;
see [Python API](api.md) for direct imports and tree-specific classes.

The low-level linter does not search for configuration files. Use the
[high-level API](api.md#validate-files-and-write-reports) for CLI-style discovery
and directory traversal.
