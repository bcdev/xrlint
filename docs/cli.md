# Command Line Interface

After installation, the `xrlint` command can be used from the terminal. 
The following are the command's options and arguments:

```
Usage: xrlint [OPTIONS] [FILES]...

  Lint the given FILES.

Options:
  --no-default-config   Disable use of default configuration from
                        xrlint.config.*
  -c, --config PATH     Use this configuration, overriding xrlint.config.*
                        config options if present
  -f, --format NAME     Use a specific output format - default: simple
  --max-warnings COUNT  Number of warnings to trigger nonzero exit code -
                        default: -1
  --version             Show the version and exit.
  --help                Show this message and exit.
```
