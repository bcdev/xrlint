# Examples

These examples build on [Getting Started](start.md). File-based examples need
the appropriate storage backend; in-memory examples need only XRLint.
The repository's [examples directory](https://github.com/bcdev/xrlint/tree/main/examples)
contains additional executable Python modules.

## Configuration

Combine core and ACDD checks, then tighten one rule for published files:

```yaml
- recommended
- acdd/recommended
- ignores: ["**/scratch/**"]
- files: ["**/published/**"]
  rules:
    var-units: error
```

Use it from the CLI with `xrlint --config config.yaml data/`.

For custom Python plugins, the repository provides two equivalent configurations:

| Example | Approach |
| --- | --- |
| [plugin_config.py](https://github.com/bcdev/xrlint/blob/main/examples/plugin_config.py) | A `Plugin` object with a rule registered by `plugin.define_rule()`. |
| [virtual_plugin_config.py](https://github.com/bcdev/xrlint/blob/main/examples/virtual_plugin_config.py) | A dictionary containing metadata, rule classes, and a named preset. |

Both define a `hello/good-title` rule that expects the title `Hello World!`, and
combine it with core recommended checks. From an installed repository checkout:

```bash
xrlint --config examples/plugin_config.py example.nc
xrlint --config examples/virtual_plugin_config.py example.nc
```

The configuration can also be passed to the Python API:

```python
import xarray as xr

from examples.plugin_config import export_config
from xrlint.linter import new_linter

dataset = xr.Dataset(attrs={"title": "Hello World!"})
result = new_linter(export_config()).validate(dataset)
assert not any(m.rule_id == "hello/good-title" for m in result.messages)
```

Other recommended rules can still report missing metadata. For a complete
standalone plugin definition, see [Custom Plugins](config.md#custom-plugins).

## Developing rules

This small rule checks only the dataset title:

```python
import xarray as xr

from xrlint.node import DatasetNode
from xrlint.rule import RuleContext, RuleOp, define_rule
from xrlint.testing import RuleTest, RuleTester


@define_rule("good-title")
class GoodTitle(RuleOp):
    """Require a greeting as the dataset title."""

    def validate_dataset(self, ctx: RuleContext, node: DatasetNode):
        if node.dataset.attrs.get("title") != "Hello World!":
            ctx.report("Expected title 'Hello World!'.")


RuleTester().run(
    "good-title",
    GoodTitle,
    valid=[RuleTest(dataset=xr.Dataset(attrs={"title": "Hello World!"}))],
    invalid=[
        RuleTest(
            dataset=xr.Dataset(),
            expected=["Expected title 'Hello World!'."],
        )
    ],
)
```

Invalid cases must supply `expected`: either a message count or a list of expected
message texts. Valid cases must omit it. For parameterized rules, pass `args`
or `kwargs` to `RuleTest`.

Use `RuleTester.define_test()` to generate a `unittest.TestCase` class discoverable
by pytest. The [rule_testing.py example](https://github.com/bcdev/xrlint/blob/main/examples/rule_testing.py)
demonstrates both approaches:

```bash
python -m examples.rule_testing
python -m pytest tests/test_examples.py
```

## API usage

Validate an in-memory dataset with a focused rule configuration:

```python
import xarray as xr
from xrlint.linter import new_linter

dataset = xr.Dataset()
linter = new_linter(rules={"no-empty-attrs": "error"})
result = linter.validate(dataset, file_path="sample.nc")

assert result.error_count == 1
for message in result.messages:
    print(message.node_path, message.message)
    for suggestion in message.suggestions or []:
        print("Suggestion:", suggestion.desc)
```

See [Validate files and write reports](api.md#validate-files-and-write-reports)
for directory traversal, JSON output, and aggregate statistics.

## Remote datasets

For S3 Zarr data, install the backend and filesystem support:

```bash
python -m pip install zarr s3fs
```

Replace the example bucket and dataset names with your data. Open a public
dataset through the low-level linter:

```python
from xrlint.linter import new_linter

linter = new_linter("recommended")
result = linter.validate(
    "s3://your-public-bucket/example.zarr",
    opener_options={
        "engine": "zarr",
        "backend_kwargs": {"storage_options": {"anon": True}},
    },
)
print(result.error_count, result.warning_count)
```

For anonymous discovery, configure the listing filesystem explicitly. CLI
directory listing does not receive dataset `opener_options`:

```python
import fsspec
from xrlint.linter import new_linter

filesystem = fsspec.filesystem("s3", anon=True)
linter = new_linter("recommended")
for store in filesystem.glob("your-public-bucket/data/*.zarr"):
    result = linter.validate(
        filesystem.unstrip_protocol(store),
        opener_options={
            "engine": "zarr",
            "backend_kwargs": {"storage_options": {"anon": True}},
        },
    )
    print(result.file_path, result.error_count, result.warning_count)
```

For authenticated sources, configure the filesystem and backend credentials
through their normal mechanisms. The repository's
[check_s3_bucket.py](https://github.com/bcdev/xrlint/blob/main/examples/check_s3_bucket.py)
demonstrates high-level traversal using the environment's S3 configuration;
it accesses the network and its bucket must be accessible to that environment.

## Multi-level datasets

To inspect xcube multi-level datasets, save this as `config.yaml`:

```yaml
- recommended
- xcube/recommended
```

Then run:

```bash
xrlint --config config.yaml data/example.levels
```

The xcube preset adds the `*.levels` file pattern, selects the multi-level
processor, and enables the associated rules. See
[Configuring Processors](config.md#configuring-processors) and
[Custom Processors](config.md#custom-processors) for the opening lifecycle.
