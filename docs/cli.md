# Command Line Interface

After installation, the `xrlint` command can be used from the terminal. 
The following are the command's options and arguments:

```
Usage: xrlint [OPTIONS] [FILES]...

  Validate the given dataset FILES.

  Reads configuration from `xrlint.config.*` if file exists and unless `--no-
  default-config` is set or `--config PATH` is provided. Then validates each
  dataset in FILES against the configuration. The validation result is dumped
  to standard output if not otherwise stated by `--output-file PATH`. The
  output format is `simple`. Other inbuilt formats are `json` and `html` which
  can by setting the `--format NAME` option.

Options:
  --no-default-config     Disable use of default configuration from
                          xrlint_config.*
  -c, --config PATH       Use this configuration, overriding xrlint_config.*
                          config options if present
  --plugin MODULE         Specify plugins. MODULE is the name of Python module
                          that defines an 'export_plugin()' function.
  --rule SPEC             Specify rules. SPEC must have format '<rule-name>:
                          <rule-config>' (note the space character).
  -o, --output-file PATH  Specify file to write report to
  -f, --format NAME       Use a specific output format - default: simple
  --color / --no-color    Force enabling/disabling of color
  --max-warnings COUNT    Number of warnings to trigger nonzero exit code -
                          default: 5
  --init                  Write initial configuration file and exit.
  --version               Show the version and exit.
  --help                  Show this message and exit.
```
