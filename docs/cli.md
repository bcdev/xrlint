# Command Line Interface

After installation, the `xrlint` command can be used from the terminal. 
The following are the command's options and arguments:

```
Usage: xrlint [OPTIONS] [FILES]...

  Validate the given dataset FILES.

  Reads configuration from `./xrlint_config.*` if such file exists and unless
  `--no_config_lookup` is set or `--config` is provided. Then validates each
  dataset in FILES against the configuration. The default dataset patters are
  `**/*.zarr` and `**/.nc`. FILES may comprise also directories. If a
  directory is not matched by any file pattern, it will be traversed
  recursively. The validation result is dumped to standard output if not
  otherwise stated by `--output-file`. The output format is `simple` by
  default. Other inbuilt formats are `json` and `html` which you can specify
  using the `--format` option.

Options:
  --no-config-lookup      Disable use of default configuration from
                          xrlint_config.*
  -c, --config FILE       Use this configuration, overriding xrlint_config.*
                          config options if present
  --print-config FILE     Print the configuration for the given file
  --plugin MODULE         Specify plugins. MODULE is the name of Python module
                          that defines an 'export_plugin()' function.
  --rule SPEC             Specify rules. SPEC must have format '<rule-name>:
                          <rule-config>' (note the space character).
  -o, --output-file FILE  Specify file to write report to
  -f, --format NAME       Use a specific output format - default: simple
  --color / --no-color    Force enabling/disabling of color
  --max-warnings COUNT    Number of warnings to trigger nonzero exit code -
                          default: 5
  --init                  Write initial configuration file and exit.
  --version               Show the version and exit.
  --help                  Show this message and exit.

```
