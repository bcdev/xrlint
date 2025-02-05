[![CI](https://github.com/bcdev/xrlint/actions/workflows/tests.yml/badge.svg)](https://github.com/bcdev/xrlint/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/bcdev/xrlint/graph/badge.svg?token=GVKuJao97t)](https://codecov.io/gh/bcdev/xrlint)
[![PyPI Version](https://img.shields.io/pypi/v/xrlint)](https://pypi.org/project/xrlint/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v0.json)](https://github.com/charliermarsh/ruff)[![GitHub License](https://img.shields.io/github/license/bcdev/xrlint)](https://github.com/bcdev/xrlint)

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

The following plugins provide XRLint's [inbuilt rules](https://bcdev.github.io/xrlint/rule-ref/):

- `xrlint.plugins.core`: implementing the rules for
  [tidy data](https://tutorial.xarray.dev/intermediate/data_cleaning/05.1_intro.html)
  and the 
  [CF-Conventions](https://cfconventions.org/cf-conventions/cf-conventions.html).
- `xrlint.plugins.xcube`: implementing the rules for 
  [xcube datasets](https://xcube.readthedocs.io/en/latest/cubespec.html).
  Note, this plugin is fully optional. You must manually configure 
  it to apply its rules. It may be moved into a separate GitHub repo later. 


