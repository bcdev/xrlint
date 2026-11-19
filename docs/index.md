# XRLint - A linter for xarray datasets

XRLint checks xarray datasets for metadata, structure, and convention issues.
Use the [CLI](cli.md) for files and directories or the [Python API](api.md) for
`xarray.Dataset` and `xarray.DataTree` objects. Its configurable rules and plugin
model are inspired by ESLint.

## Features

- Rules for dataset metadata, coordinates, variables, and tree groups.
- YAML, JSON, or Python configuration, including file-specific settings.
- Local files and remote sources supported by installed xarray backends and
  fsspec filesystem implementations.
- Text, JSON, and HTML reports, with rich result display in notebooks.
- Custom rules, plugins, processors, and reusable configurations.

XRLint reports findings and suggestions; it does not automatically modify
datasets. Its rules check selected convention requirements and do not establish
complete compliance with a convention.

## Built-in Rules

The [Rule Reference](rule-ref.md) describes all rules discovered during the
documentation build, including their options and preset membership.

| Plugin | Scope | Preset |
| --- | --- | --- |
| `core` | General dataset quality and selected CF convention checks | `recommended` |
| `xcube` | xcube dataset structure, including multi-level datasets | `xcube/recommended` |
| `acdd` | Attribute Convention for Data Discovery metadata, with versioned presets | `acdd/recommended` |

Installed plugins load automatically. Their rules run only when enabled by
configuration; plugin presets can be combined:

```yaml
- recommended
- xcube/recommended
- acdd/recommended
```

## Where to start

Follow [Getting Started](start.md) to install XRLint and validate a small dataset.
Then use [Configuration](config.md) to select rules for your project.
[Examples](examples.md) covers custom rules, processors, and remote datasets.
See [About](about.md) for contribution and build instructions and
[Development Notes](todo.md) for current limitations and possible future work.
