# Getting Started

## Installation

```bash
pip install xrlint
```

or

```bash
conda install -c conda-forge xrlint
```


## Command line interface 

Get basic help:

```bash
xrlint --help
```

Initializing a new project with

```bash
xrlint --init
```

writes a configuration file `xrlint_config.yaml` 
into the current working directory:

```yaml
- recommended
```

This configuration file tells XRLint to use the predefined configuration
named `recommended`.  

Create a dataset to test XRLint:

```bash
python
>>> import xarray as xr
>>> test_ds = xr.Dataset(attrs={"title": "Test Dataset"})
>>> test_ds.to_zarr("test.zarr") 
>>> exit()
```

And run XRLint:

```bash
xrlint test.zarr 
```

You can now override the predefined settings by adding your custom
rule configurations:

```yaml
- recommended
- rules:
    no-empty-attrs: off
    var-units-attr: warn
    grid-mappings: error
```

You can add rules from plugins as well:

```yaml
- recommended
- plugins:
    xcube: xrlint.plugins.xcube
- xcube/recommended  
```

And customize its rules, if desired:

```yaml
- recommended
- plugins:
    xcube: xrlint.plugins.xcube
- xcube/recommended  
- rules:
    xcube/grid-mapping-naming: off
    xcube/lat-lon-naming: warn
```

Note the prefix `xcube/` used for the rule names.

## Python API

The easiest approach to use the Python API is to import `xrlint.all`.
It contains all the public definitions from the `xrlint` package.

```python
import xrlint.all as xrl
```

Start by creating a linter with recommended settings 
using the `new_linter()` function .

```python
import xarray as xr
import xrlint.all as xrl

test_ds = xr.Dataset(attrs={"title": "Test Dataset"})

linter = xrl.new_linter("recommended")
linter.validate(test_ds)
```
