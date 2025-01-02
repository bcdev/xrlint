[![CI](https://github.com/bcdev/xrlint/actions/workflows/tests.yml/badge.svg)](https://github.com/bcdev/xrlint/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/bcdev/xrlint/graph/badge.svg?token=GVKuJao97t)](https://codecov.io/gh/bcdev/xrlint)
[![PyPI Version](https://img.shields.io/pypi/v/xrlint)](https://pypi.org/project/xrlint/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![GitHub License](https://img.shields.io/github/license/bcdev/xrlint)](https://github.com/bcdev/xrlint)

# XRLint - A linter for xarray datasets


XRLint is a [linting](https://en.wikipedia.org/wiki/Lint_(software)) 
tool and library for [xarray]() datasets.
Its design is heavily inspired by [ESLint](https://eslint.org/).

**IMPORTANT NOTE**: This project just started and is under development, 
there is no stable release yet. See 
[to-do list](docs/todo.md).

## Features 

- Flexible validation for `xarray.Dataset` objects by configurable _rules_.
- Available from _CLI_ and _Python API_.
- _Custom plugins_ providing _custom rule_ sets allow addressing 
  different dataset conventions.
- _Project-specific configurations_ including configuration of individual 
  rules and file-specific settings.

## Inbuilt Rules

The following rule plugins are currently built into the code base:

- `xrlint.plugins.core`: Implementing the rules for
  [tiny data](https://tutorial.xarray.dev/intermediate/data_cleaning/05.1_intro.html)
  and the 
  [CF-Conventions](https://cfconventions.org/cf-conventions/cf-conventions.html).
- `xrlint.plugins.core`: Implementing the rules for 
  [xcube datasets](https://xcube.readthedocs.io/en/latest/cubespec.html).
  Note, this plugin is fully optional. You must manually configure 
  it to apply its rules. It may be moved into a separate GitHub repo 
  once XRLint is mature enough. 

