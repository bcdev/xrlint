# Command Line Interface

After installation, the `xrlint` command can be used from the terminal. 
The following are the command's usage help including a short description 
of its options and arguments:

```
Usage: xrlint [OPTIONS] [FILES]...

  Validate the given dataset FILES.

  When executed, XRLint does the following three things:

  (1) Unless options '--no-config-lookup' or '--config' are used it searches
  for a default configuration file in the current working directory. Default
  configuration files are determined by their filename, namely
  'xrlint_config.py' or 'xrlint-config.<format>', where <format> refers to the
  filename extensions 'json', 'yaml', and 'yml'. A Python configuration file
  ('*.py'), is expected to provide XRLInt configuration from a function
  'export_config()', which may include custom plugins and rules.

  (2) It then validates each dataset in FILES against the configuration. The
  default dataset patters are '**/*.zarr' and '**/.nc'. FILES may comprise
  also directories or URLs. The supported URL protocols are the ones supported
  by xarray. Using remote protocols may require installing additional packages
  such as S3Fs (https://s3fs.readthedocs.io/) for the 's3' protocol. If a
  directory is provided that not matched by any file pattern, it will be
  traversed recursively.

  (3) The validation result is dumped to standard output if not otherwise
  stated by '--output-file'. The output format is 'simple' by default. Other
  inbuilt formats are 'json' and 'html' which you can specify using the '--
  format' option.

  Please refer to the documentation (https://bcdev.github.io/xrlint/) for more
  information.

Options:
  --no-config-lookup      Disable use of default configuration files
  -c, --config FILE       Use this configuration instead of looking for a
                          default configuration file
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
