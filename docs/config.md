# Configure XRLint

_**Note**: this chapter's material is based on the documentation of how to [configure ESLint](https://eslint.org/docs/latest/use/configure/).
Many parts have been copied and adjusted as it applies in many similar ways to XRLint._ 

## Configuration File

The XRLint configuration file may be named any of the following:

* `xrlint_config.yaml`
* `xrlint_config.json`
* `xrlint_config.py`

It should be placed in the root directory of your project and export 
an array of [configuration objects](#configuration-objects) or 
references to [predefined configuration objects](#predefined-configuration-objects). 

Here’s a YAML example:

```yaml
- files: ["**/*.zarr", "**/*.nc"]
- plugins:
    xcube: xrlint.plugins.xcube
- recommended
- xcube/recommended
```

Same using JSON:

```json
[
  {"files": ["**/*.zarr", "**/*.nc"]},
  {
    "plugins": {
      "xcube": "xrlint.plugins.xcube"
    }
  },
  "recommended",
  "xcube/recommended"
]
```

And as Python script:

```python
def export_configs():
    return [
      {"files": ["**/*.zarr", "**/*.nc"]},
      {
        "plugins": {
          "xcube": "xrlint.plugins.xcube"
        }
      },
      "recommended",
      "xcube/recommended"
    ]
```


## Configuration Objects

Each configuration object contains all of the information XRLint needs 
to execute on a set of files. Each configuration object is made up of 
these properties:

* `name` - A name for the configuration object. 
  This is used in error messages and config inspector to help identify which 
  configuration object is being used.
* `files` - A list of glob patterns indicating the files that the 
  configuration object should apply to. If not specified, the configuration 
  object applies to all files matched by any other configuration object.
  See section [File and Ignore Patterns](#file-and-ignore-patterns) below.
* `ignores` - A list of glob patterns indicating the files that the 
  configuration object should not apply to. If not specified, the configuration 
  object applies to all files matched by files. If ignores is used without any 
  other keys in the configuration object, then the patterns act as _global ignores_.
  See section [File and Ignore Patterns](#file-and-ignore-patterns) below.
* `opener_options` - A dictionary specifying keyword-arguments that are passed 
  directly to the `xarray.open_dataset()` function. The available options are 
  dependent on the xarray backend selected by the `engine` option.
  See section [Opener Options](#opener-options) below.
* `linter_options` - A dictionary containing settings related to 
  the linting process. (Currently not used.)
  See section [Linter Options](#linter-options) below.
* `settings` - An object containing name-value pairs of information that should 
  be available to all rules.
* `plugins` - A dictionary containing a name-value mapping of plugin names 
  to either plugin module names or `Plugin` objects. When `files` is specified, 
  these plugins are only available to the matching files.
  See sections [Configuring Plugins](#configuring-plugins) 
  and [Custom Plugins](#custom-plugins) below.
* `rules` - An object containing the configured rules. 
  When `files` or `ignores` are specified, these rule configurations are only 
  available to the matching files.
  See sections [Configuring Rules](#configuring-rules) 
  and [Custom Rules](#custom-rules) below.
* `processor` - A string indicating the name of a processor inside of a plugin, 
  i.e., `"<plugin-name>/<processor-name>"`. In Python configurations 
  it can also be an object of type `ProcessorOp` containing
  `preprocess()` and `postprocess()` methods.
  See sections [Configuring Processors](#custom-processors) 
  and [Custom Processors](#custom-processors) below.

## File and Ignore Patterns

_Coming soon_

## Opener Options

_Coming soon_

## Linter Options

_Coming soon_

## Configuring Plugins

_Coming soon_

## Configuring Rules

_Coming soon_

## Configuring Processors

_Coming soon_

## Predefined Configuration Objects

_Coming soon_

## Custom Plugins

_Coming soon_

## Custom Rules

_Coming soon_

## Custom Processors

_Coming soon_

