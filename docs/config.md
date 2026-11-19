# Configure XRLint

XRLint uses an ordered list of configuration objects and named presets.
The CLI and Python API share this model. Loading a plugin makes its rules
available; a preset or `rules` entry enables them.

## Configuration File

Run `xrlint --init` to create `xrlint-config.yaml` containing `- recommended`.
Without `--config`, the CLI looks in the **current working directory only**,
using the first file it finds in this order:

1. `xrlint-config.yaml`
2. `xrlint-config.yml`
3. `xrlint-config.json`
4. `xrlint_config.yaml` (legacy name)
5. `xrlint_config.yml` (legacy name)
6. `xrlint_config.json` (legacy name)
7. `xrlint_config.py`

It does not search parent directories or dataset directories.
Use `xrlint --config path/to/config.yaml data/` for an explicit file, or
`--no-config-lookup` to disable discovery. There is no implicit recommended
configuration: a run that loads no rules fails with `no rules configured`.

These configurations are equivalent. The installed `xcube` plugin is
discovered automatically.

```yaml
- recommended
- xcube/recommended
- rules:
    xcube/grid-mapping-naming: "off"
```

```json
[
  "recommended",
  "xcube/recommended",
  {"rules": {"xcube/grid-mapping-naming": "off"}}
]
```

A Python file must define `export_config()`:

```python
def export_config():
    return [
        "recommended",
        "xcube/recommended",
        {"rules": {"xcube/grid-mapping-naming": "off"}},
    ]
```

Python configurations can also contain plugin objects and processor instances.

## Configuration Objects

Each object can contain the following optional properties:

| Property | Purpose |
| --- | --- |
| `name` | A descriptive label for the object. |
| `files` | Patterns selecting paths to which this object applies. |
| `ignores` | Patterns excluding paths from this object. |
| `opener_options` | Keyword arguments for opening datasets. |
| `linter_options` | Reserved for linting options; currently has no effect. |
| `settings` | Shared values available to rules through `ctx.settings`. |
| `plugins` | Mapping from namespaces to plugin module names, objects, or definitions. |
| `rules` | Mapping from rule identifiers to severities and arguments. |
| `processor` | A `"namespace/processor-name"` reference or Python `ProcessorOp` instance. |

Objects without file filters apply to every selected dataset. Matching objects
merge from first to last. Later rule severities override earlier ones; different
rule identifiers accumulate. Option dictionaries merge by key, including nested
dictionaries; option lists merge by index. A later plugin under the same
namespace replaces the earlier plugin. A later non-null processor replaces the
earlier processor.

Rule arguments have a specific merge rule: when severity stays the same,
positional arguments merge by index and keyword arguments merge by key.
When severity changes, the later rule configuration replaces the earlier one,
including its arguments. Repeat arguments you want to retain when changing
severity.

Inspect the merged configuration with:

```bash
xrlint --print-config data/example.nc
```

This does not open the dataset. It inspects configuration, but does not check
whether the CLI's global file filter will select the path.

## File and Ignore Patterns

The CLI first selects dataset paths using a global file filter, then merges
the configuration objects that apply to each selected path.

- Default included patterns are `**/*.nc` and `**/*.zarr`.
- An object containing only `files` and/or `ignores` (optionally with a `name`)
  contributes to the global filter. Its `files` patterns **add to** the defaults.
- An object that also contains rules, settings, a processor, or other options
  filters only that object's contribution. Its `ignores` do not exclude the
  dataset from the whole run.
- Directories not selected as datasets are walked recursively. A selected Zarr
  store is treated as one dataset. To exclude a subtree, match its descendants.

For example, add HDF5 files, exclude generated data, and make missing units an
error only in published datasets:

```yaml
- files: ["**/*.h5"]
- ignores: ["**/generated/**"]
- recommended
- files: ["**/published/**"]
  rules:
    var-units: error
```

Adding an extension does not install an xarray backend. To validate only NetCDF
files, pass those files explicitly or exclude other recognized formats, for
example with `ignores: ["**/*.zarr"]`.

Patterns match the whole supplied path or URL; they are not rebased to the
configuration file. Paths found during traversal may be absolute. Use `/`
separators and patterns such as `**/published/**` when the leading path is not
fixed, including on Windows.

| Syntax | Meaning |
| --- | --- |
| `*` | Zero or more characters other than `/`. |
| `**` | Zero or more characters, including `/`. |
| `**/` | Also matches paths without a leading directory. |
| `?` | One character. |
| `#text` | A comment pattern; ignored. |
| `!pattern` | Negation; in `ignores`, can re-include a matching excluded path. |

This is a small glob implementation, not full minimatch or Git ignore syntax.
Brace expansion and character classes are unsupported. A trailing slash does
not mean "all descendants": use `**/cache/**`, not just `cache/`.
The built-in ignore names `.git` and `node_modules` are exact patterns; use
`**/.git/**` and `**/node_modules/**` for subtree exclusions.

For a simple ignore exception, place the negation immediately after its exclusion:

```yaml
- ignores: ["**/scratch/**", "!**/scratch/reference.nc"]
- recommended
```

Pass directories or concrete paths as CLI arguments. Glob patterns belong in
configuration; XRLint does not expand wildcard arguments itself.

The low-level `Linter.validate()` API computes matching configuration directly;
it does not perform CLI discovery or split out global filters. Use
`XRLint.validate_files()` for the CLI's file-selection behavior.

## Opener Options

For a source, XRLint tries `xarray.open_datatree()` first and falls back to
`xarray.open_dataset()` if that fails with a supported opening error. It selects
`engine="zarr"` for `.zarr` paths unless an engine is supplied.
`opener_options` provides keyword arguments to these openers:

```yaml
- recommended
- files: ["**/*.nc"]
  opener_options:
    engine: netcdf4
    decode_times: true
```

Available options depend on your installed xarray version and backend. Keep
decoding enabled unless your rules are designed for undecoded data.
Opening options have no effect on existing `xr.Dataset` or `xr.DataTree` objects.

For a public S3 Zarr dataset, opening options can include:

```yaml
- recommended
- files: ["s3://**/*.zarr"]
  opener_options:
    engine: zarr
    backend_kwargs:
      storage_options:
        anon: true
```

Install `zarr` and `s3fs` for this example. These storage options go to the
dataset opener. CLI directory listing uses a separate fsspec filesystem and
does not receive `opener_options`; for anonymous bucket traversal see
[Examples](examples.md#remote-datasets).

When a processor is selected, it receives `opener_options` and controls opening.
The default opener closes datasets it opens; processors manage their resources.

## Linter Options

`linter_options` is accepted and merged, but no options are currently consumed.
Omit it. Warning limits, formats, and output paths belong to
[CLI options](cli.md) or the `XRLint` constructor.

Use `settings` for information shared by custom rules:

```yaml
- recommended
- settings:
    institution: Example Research Institute
```

A custom rule reads this as `ctx.settings.get("institution")`.
Settings have no effect unless a rule uses them.

## Configuring Plugins

The CLI and `new_linter()` discover installed plugins from the `xrlint.rules`
entry-point group. An installed XRLint distribution supplies `core`, `xcube`,
and `acdd`. Discovery does not enable their rules.

Core rule identifiers omit the namespace, as in `var-units`. Internally, the
core plugin is registered as `__core__`, which appears in printed configuration;
`core/` is not its namespace. Other plugins
use identifiers such as `xcube/dataset-title` or `acdd/1.3-conventions`.
Named presets follow the same convention: `recommended` selects core rules;
`acdd/recommended` selects ACDD rules.

For plugins without an entry point, register an importable module explicitly:

```yaml
- plugins:
    project: my_project.xrlint_plugin
- project/recommended
```

The module must export `export_plugin()`. Put its registration before references
to its presets. Python configurations can instead supply a `Plugin` instance
or a dictionary defining a virtual plugin. The mapping key is the namespace
used in rule identifiers; use a consistent namespace in presets too.

`--plugin MODULE` makes a module's rules available using its `meta.name` as the
namespace. Register custom plugins in the configuration file itself if that file
references their presets: the file is resolved before CLI plugin registrations
are merged.

## Configuring Rules

| Value | Numeric equivalent | Effect |
| --- | --- | --- |
| `"off"` | `0` | Disable the rule. |
| `"warn"` | `1` | Emit warnings; the CLI warning limit determines failure. |
| `"error"` | `2` | Emit errors; any error fails a CLI validation run. |

Quote `"off"` in YAML to keep it a string rather than a YAML boolean.
A rule's category (`problem`, `suggestion`, or `layout`) does not determine its
severity. See the [Rule Reference](rule-ref.md) for identifiers and options.

To configure arguments, use a list starting with severity. Remaining items
are positional arguments, except that a final dictionary becomes keyword
arguments to the rule operation's constructor:

```yaml
- recommended
- rules:
    no-empty-attrs: "off"
    var-units: error
    access-latency: [warn, {threshold: 5.0}]
    conventions: [error, {match: "^CF-"}]
    var-desc: [warn, {attrs: [long_name]}]
    content-desc: [warn, {skip_vars: true}]
```

For example, `[warn, 5.0]` also supplies the `access-latency` threshold
positionally. The `content-desc` option is named `skip_vars`.

Schemas describe supported arguments, but XRLint does not yet validate
arguments against them before constructing a rule. Invalid names or types
may cause an exception or be ignored by the rule implementation.

CLI `--rule` entries are appended after the file configuration:

```bash
xrlint --rule "var-units: error" --rule "access-latency: [warn, {threshold: 5.0}]" data/
```

## Configuring Processors

A processor opens a source as zero or more datasets, then combines their
validation messages. It applies only to sources, not existing in-memory xarray
objects. Each selected path uses at most one processor.

The `xcube/recommended` and `xcube/all` presets already recognize `*.levels`
directories and select `xcube/multi-level-dataset`. To select it explicitly:

```yaml
- files: ["**/*.levels"]
- recommended
- files: ["**/*.levels"]
  processor: xcube/multi-level-dataset
```

The filter-only object adds the extension to CLI discovery. The processor reads
levels and optional `.zlevels` metadata. Use `xcube/recommended` as well to enable
checks specific to multi-level datasets.

## Predefined Configuration Objects

Presets expand into configuration objects at their position in the list.
Combine presets and place overrides after them.

| Preset | Contents |
| --- | --- |
| `recommended` | Core checks with warnings and errors; `no-empty-chunks` is disabled. |
| `all` | All core rules at error severity. |
| `xcube/recommended` | xcube checks plus discovery and processing of `*.levels` datasets. |
| `xcube/all` | All xcube rules at error severity, with the same multi-level setup. |
| `acdd/recommended` or `acdd/acdd_1.3` | ACDD 1.3: conventions and highly recommended attributes are errors; other checks are warnings. |
| `acdd/acdd_1.3_strict` | All included ACDD 1.3 checks are errors. |
| `acdd/acdd_1.3_warn` | All included ACDD 1.3 checks are warnings. |
| `acdd/acdd_1.1` | Exported preset, but its rule implementations are missing in 0.6.0; see below. |
| `acdd/acdd_1.0` | ACDD 1.0 attribute presence checks. |

Plugin presets do not implicitly enable core rules. To combine core and ACDD:

```yaml
- recommended
- acdd/recommended
```

In version 0.6.0, `acdd/acdd_1.1` references three `acdd/1.1-attrs-*` rules that
are not registered. Selecting it produces unknown-rule errors. The 1.0 and 1.3
presets have registered rule implementations; choose the version appropriate
to your data.

Version 0.6.0 also exports `acdd/acdd_1.3_strict_recommended`, but it contains an
unprefixed `1.3-attrs-recommended` rule identifier that resolves incorrectly.
Use this working configuration instead:

```yaml
- acdd/recommended
- rules:
    acdd/1.3-attrs-recommended: error
```

## Custom Plugins

Save this complete Python configuration as `xrlint_config.py`:

```python
from xrlint.node import DatasetNode
from xrlint.plugin import new_plugin
from xrlint.rule import RuleContext, RuleOp

plugin = new_plugin(name="project", version="1.0.0")


@plugin.define_rule("required-title")
class RequiredTitle(RuleOp):
    """Require a specific dataset title."""

    def __init__(self, title: str = "Example dataset"):
        self.title = title

    def validate_dataset(self, ctx: RuleContext, node: DatasetNode):
        if node.dataset.attrs.get("title") != self.title:
            ctx.report(
                f"Expected dataset title {self.title!r}.",
                suggestions=[f"Set the title attribute to {self.title!r}."],
            )


plugin.define_config(
    "recommended", {"rules": {"project/required-title": "error"}}
)


def export_plugin():
    return plugin


def export_config():
    return [
        {"plugins": {"project": plugin}},
        "recommended",
        "project/recommended",
    ]
```

Run `xrlint --config xrlint_config.py data/`. An explicit path avoids a
previously created YAML file taking precedence over the Python file.

For a separately packaged plugin, put the plugin and `export_plugin()` in an
importable module, such as `my_project.xrlint_plugin`, and declare:

```toml
[project.entry-points."xrlint.rules"]
project = "my_project.xrlint_plugin"
```

After installation, discovery uses `plugin.meta.name`. Keep the entry-point
name, metadata name, and preset namespace consistent. The entry point targets
a module with `export_plugin()`, not the function itself.

See [Examples](examples.md#configuration) for a dictionary-based virtual plugin.

## Custom Rules

Derive from `RuleOp` and register the class with
`@plugin.define_rule("rule-name")`, as above, or use `@define_rule(...)`
and add it to a plugin's rules dictionary.

| Callback | Receives |
| --- | --- |
| `validate_datatree(ctx, node)` | A `DataTreeNode` for a tree group. |
| `validate_dataset(ctx, node)` | A `DatasetNode` exposing `node.dataset`. |
| `validate_variable(ctx, node)` | A `VariableNode` exposing `node.array` and `node.name`. |
| `validate_attrs(ctx, node)` | An `AttrsNode` exposing an attribute mapping. |
| `validate_attr(ctx, node)` | An `AttrNode` exposing an attribute name and value. |

Dataset traversal visits the dataset, global attributes, coordinate variables,
and data variables, including each variable's attributes. Each rule gets its
own traversal. Tree traversal validates group nodes and visits dataset contents
at leaves; a tree without children is treated as a dataset. Contents attached
to non-leaf groups are not independently traversed as datasets.

Use `ctx.report()` to emit a message with the current rule identifier, severity,
and node path. Rules should not depend on the configured severity.
`ctx.settings` provides shared values; during dataset callbacks, `ctx.dataset`
is the current dataset. `ctx.access_latency` is measured opening time, or
`None` for in-memory inputs.

Raise `RuleExit` to stop the current rule's entire traversal. A normal `return`
skips only the current callback. Suggestions are accessible from
`Message.suggestions`; automatic fixes are not implemented.

See [Developing rules](examples.md#developing-rules) for `RuleTester` examples
and the [Rule API](api.md#rule-api) for the interfaces.

## Custom Processors

Subclass `ProcessorOp` and implement both methods:

- `preprocess(file_path, opener_options)` returns a list of
  `(xr.Dataset | xr.DataTree, path)` pairs.
- `postprocess(messages, file_path)` receives one message list per returned
  dataset and returns the final flat message list.

This processor can be added to the custom plugin above. It loads a dataset into
memory and closes its file before returning:

```python
import xarray as xr

from xrlint.processor import ProcessorOp


@plugin.define_processor("loaded-dataset")
class LoadedDataset(ProcessorOp):
    def preprocess(self, file_path, opener_options):
        with xr.open_dataset(file_path, **dict(opener_options)) as dataset:
            dataset.load()
        return [(dataset, file_path)]

    def postprocess(self, messages, file_path):
        return [message for group in messages for message in group]
```

Append this object to `export_config()`'s returned list:

```python
{"files": ["**/*.nc"], "processor": "project/loaded-dataset"}
```

Loading the entire dataset suits small examples; production processors should
choose resource management appropriate to their data. XRLint does not close
datasets returned by processors. A named processor is constructed without
arguments. Use `opener_options` for opening settings or supply a configured
processor instance directly in a Python configuration.
