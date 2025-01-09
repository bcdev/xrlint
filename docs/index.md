# XRLint - A linter for xarray datasets


XRLint is a [linting](https://en.wikipedia.org/wiki/Lint_(software)) 
tool and library for [xarray]() datasets.
Its design is heavily inspired by [ESLint](https://eslint.org/).


## Features 

- Flexible validation for `xarray.Dataset` objects by configurable rules.
- Available from CLI and Python API.
- Custom plugins providing custom rule sets allow addressing 
  different dataset conventions.
- Project-specific configurations including configuration of individual 
  rules and file-specific settings.


## Inbuilt Rules

The following rule plugins are currently built into the code base:

- `core`: Implementing the rules for
  [tidy data](https://tutorial.xarray.dev/intermediate/data_cleaning/05.1_intro.html)
  and the 
  [CF-Conventions](https://cfconventions.org/cf-conventions/cf-conventions.html).
- `xcube`: Implementing the rules for 
  [xcube datasets](https://xcube.readthedocs.io/en/latest/cubespec.html).
  Note, this plugin is fully optional. You must manually configure 
  it to apply its rules. It may be moved into a separate GitHub repo 
  once XRLint is mature enough. 

