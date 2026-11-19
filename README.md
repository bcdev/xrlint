[![CI](https://github.com/bcdev/xrlint/actions/workflows/tests.yml/badge.svg)](https://github.com/bcdev/xrlint/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/bcdev/xrlint/graph/badge.svg)](https://codecov.io/gh/bcdev/xrlint)
[![PyPI Version](https://img.shields.io/pypi/v/xrlint)](https://pypi.org/project/xrlint/)
[![Conda Version](https://anaconda.org/conda-forge/xrlint/badges/version.svg)](https://anaconda.org/conda-forge/xrlint)
[![GitHub License](https://img.shields.io/github/license/bcdev/xrlint)](LICENSE)

# XRLint - A linter for xarray datasets

XRLint checks xarray datasets for metadata, structure, and convention issues.
Use it from the command line to check dataset files, or from Python to validate
`xarray.Dataset` and `xarray.DataTree` objects. Its configurable rules and plugin
model are inspired by ESLint.

## Features

- Configurable rules for dataset metadata, coordinates, variables, and groups.
- YAML, JSON, and Python configurations with file-specific overrides.
- Local datasets and remote sources supported by the installed xarray backends
  and fsspec filesystem implementations.
- Text, JSON, and HTML reports, plus notebook rendering of results.
- Custom rules, plugins, processors, and reusable configurations.

XRLint reports findings and suggestions; it does not automatically modify data.
Its built-in rules cover selected convention requirements, not full compliance
certification.

## Quick start

Requires Python 3.10 or newer. Install XRLint and a backend for your data:

```bash
python -m pip install xrlint netCDF4
xrlint --init
xrlint data/example.nc
```

For Zarr datasets, install `zarr` too. The initial configuration enables the core
`recommended` preset. No rules are enabled automatically without configuration.

To validate an in-memory dataset:

```python
import xarray as xr
from xrlint.linter import new_linter

dataset = xr.Dataset(attrs={"title": "Example dataset"})
result = new_linter("recommended").validate(dataset)

for message in result.messages:
    print(message.rule_id, message.node_path, message.message)

print(f"{result.error_count} errors, {result.warning_count} warnings")
```

This deliberately minimal dataset produces metadata warnings.
See [Getting Started](https://bcdev.github.io/xrlint/start/) for a complete
file-based example and installation alternatives.

## Built-in plugins

All three plugins are discovered when XRLint is installed. Select their presets
or individual rules to enable checks.

| Plugin | Scope | Preset |
| --- | --- | --- |
| `core` | General dataset quality and selected CF convention checks | `recommended` |
| `xcube` | xcube dataset structure and multi-level datasets | `xcube/recommended` |
| `acdd` | Attribute Convention for Data Discovery (ACDD) metadata | `acdd/recommended` |

For example, enable core and ACDD checks in `xrlint-config.yaml`:

```yaml
- recommended
- acdd/recommended
- rules:
    var-units: error
```

## Documentation and contributing

- [Getting Started](https://bcdev.github.io/xrlint/start/)
- [Configuration](https://bcdev.github.io/xrlint/config/)
- [Rule Reference](https://bcdev.github.io/xrlint/rule-ref/)
- [CLI](https://bcdev.github.io/xrlint/cli/) and [Python API](https://bcdev.github.io/xrlint/api/)
- [Examples](https://bcdev.github.io/xrlint/examples/)
- [Change history](CHANGES.md)

Report bugs or request features through [GitHub issues](https://github.com/bcdev/xrlint/issues).
See [CONTRIBUTING.md](CONTRIBUTING.md) for development and documentation setup,
and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

XRLint is distributed under the [MIT License](LICENSE).
