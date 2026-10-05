# Contributing to XRLint

We welcome code, documentation, bug reports, and ideas. Please follow our
[Code of Conduct](CODE_OF_CONDUCT.md).
Use [GitHub issues](https://github.com/bcdev/xrlint/issues) for bugs and proposals,
and submit changes through a [pull request](https://github.com/bcdev/xrlint/pulls).
Code and configuration changes must be linked to a corresponding issue.

## Development setup

Use Python 3.10 or newer. From the repository root, install the project in
editable mode with development and documentation dependencies:

```bash
python -m pip install -e ".[dev,doc]"
```

An editable installation also registers the `xrlint` command and built-in plugin
entry points. Merely adding the source directory to `PYTHONPATH` does not register
those entry points.

If using conda or mamba, create and activate the repository environment, then
install the project and extras to include dependencies declared in
`pyproject.toml`:

```bash
conda env create -f environment.yml
conda activate xrlint
python -m pip install -e ".[dev,doc]"
```

## Project layout

| Path | Responsibility |
| --- | --- |
| `xrlint/cli/` | Click command, configuration discovery, file traversal, and reporting. |
| `xrlint/linter.py`, `xrlint/_linter/` | Linter configuration, opening, traversal, and rule execution. |
| `xrlint/config.py` | Configuration conversion, plugin discovery, and merging. |
| `xrlint/rule.py`, `node.py`, `plugin.py`, `processor.py` | Extension interfaces and metadata. |
| `xrlint/plugins/` | Core, xcube, and ACDD rules and presets. |
| `xrlint/formatters/` | Text, JSON, and HTML reports. |
| `tests/` | Tests mirroring the package structure. |
| `examples/` | Custom configurations and API examples. |
| `docs/` | MkDocs pages and the rule-reference generator. |

## Checks before submitting

Run the checks relevant to your change from the repository root:

```bash
python -m ruff format --check
python -m ruff check
python -m pytest --cov=xrlint --cov-branch --cov-report=html
python -m mkdocs build --strict
```

- Keep existing tests passing and add coverage for new or changed behavior.
- Aim to keep coverage close to 100%; review the report in `htmlcov/index.html`.
- Update documentation and examples when behavior or configuration changes.
- For documentation changes, preview the site with `python -m mkdocs serve`
  and verify links, code blocks, and generated references.
- Describe the problem, resulting behavior, and validation in the pull request.

## Code style

Use Ruff's formatter and linter with the repository configuration:

```bash
python -m ruff format
python -m ruff check
```

Group imports in this order: future imports, standard library, third-party
packages, absolute XRLint imports, and local relative imports. The repository
configures isort with the Black profile. Same-package imports such as
`from .module import name` are acceptable; avoid parent-relative imports such as
`from ..module import name`.

Use `typing.TYPE_CHECKING` for type-only imports to avoid circular dependencies.
Document public APIs with Google-style docstrings.

## Contributing a rule

Choose a lowercase, hyphen-separated name describing a single requirement.
Prefix prohibitions with `no-`, as in `no-empty-attrs`. Plugin namespaces are
separated with a slash in configuration, such as `xcube/cube-dims-order`.

Place the implementation in
`xrlint/plugins/<plugin>/rules/<rule_name>.py`, replacing hyphens with underscores.
Derive from `RuleOp`, register with `plugin.define_rule()`, and implement only
the callbacks needed. Keep the reason for each rule easy to explain.

Provide a description, version, relevant documentation URL, and a schema for
any options. Schemas currently document options; runtime schema validation is
not implemented. Keep constructor arguments and schema metadata consistent.
Decide explicitly whether the rule belongs in a recommended preset.

Place tests in `tests/plugins/<plugin>/rules/test_<rule_name>.py`.
Use `RuleTester` with valid and invalid datasets, including parameter cases when
applicable. See the [rule development examples](docs/examples.md#developing-rules)
and [extension guide](docs/config.md#custom-rules).

## Contributing a plugin

Plugins contribute rules, processors, and named configurations. An importable
plugin module must define `export_plugin()` returning a `Plugin` object.
For automatic discovery, declare an entry point in the plugin package:

```toml
[project.entry-points."xrlint.rules"]
my_plugin = "my_package.xrlint_plugin"
```

The entry point targets the module, not its factory function. Use a consistent
entry-point name, `PluginMeta.name`, and rule namespace. Install the package to
register the entry point. Discovery makes rules available; users still enable
them through presets or rule configuration.

Local Python configurations can use a plugin directly without packaging.
See [Custom Plugins](docs/config.md#custom-plugins).

## Building documentation

```bash
python -m mkdocs build --strict
python -m mkdocs serve
```

The build writes `site/`. The preview command serves the site locally and
rebuilds when files change. Edit Markdown pages in `docs/`; update `mkdocs.yml`
when adding navigation entries.

`docs/mkruleref.py` runs automatically through `mkdocs-gen-files`, generating
`rule-ref.md` from discovered plugin metadata. Do not create or edit that
generated page manually. Update rule descriptions and schemas in the source,
or change the generator for presentation changes. The API page uses
`mkdocstrings` to render source docstrings.

The plugins installed in the build environment determine the generated rule
reference. Use a project environment without unrelated third-party XRLint
plugins when building the project's published documentation.
