# XRLint - A linter for xarray datasets


XRLint is a [linting](https://en.wikipedia.org/wiki/Lint_(software)) 
tool and library for [xarray]() datasets.
Its design is heavily inspired by the awesome [ESLint](https://eslint.org/).


## Features 

- Flexible validation for `xarray.Dataset` objects by configurable rules.
- Available from CLI and Python API.
- Custom plugins providing custom rule sets allow addressing 
  different dataset conventions.
- Project-specific configurations including configuration of individual 
  rules and file-specific settings.
- Works with dataset files in the local filesystem or any of the remote 
  filesystems supported by xarray.


## Inbuilt Rules

The following plugins provide XRLint's [inbuilt rules](rule-ref.md):

- `core`: implementing the rules for
  [tidy data](https://tutorial.xarray.dev/intermediate/data_cleaning/05.1_intro.html)
  and the 
  [CF-Conventions](https://cfconventions.org/cf-conventions/cf-conventions.html).
- `xcube`: implementing the rules for 
  [xcube datasets](https://xcube.readthedocs.io/en/latest/cubespec.html).
  Note, this plugin is fully optional. You must manually configure 
  it to apply its rules. It may be moved into a separate GitHub repo later. 

