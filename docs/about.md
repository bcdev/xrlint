# About XRLint

## Changelog

You can find the complete XRLint changelog 
[here](https://github.com/bcdev/xrlint/blob/main/CHANGES.md). 

## Reporting

If you have suggestions, ideas, feature requests, or if you have identified
a malfunction or error, then please 
[post an issue](https://github.com/bcdev/xrlint/issues). 

## Contributions

The XRLint project welcomes contributions of any form
as long as you respect our 
[code of conduct](https://github.com/bcdev/xrlint/blob/main/CODE_OF_CONDUCT.md)
and follow our 
[contribution guide](https://github.com/bcdev/xrlint/blob/main/CONTRIBUTING.md).

If you'd like to submit code or documentation changes, we ask you to provide a 
pull request (PR) 
[here](https://github.com/bcdev/xrlint/pulls). 
For code and configuration changes, your PR must be linked to a 
corresponding issue. 

## Development

To set up development environment, with repository root as current
working directory:

```bash
pip install .[dev,doc]
```

### Testing and Coverage

XRLint uses [pytest](https://docs.pytest.org/) for unit-level testing 
and code coverage analysis.

```bash
pytest --cov=xrlint --cov-report html
```

### Code Style

XRLint source code is formatted using the [black](https://black.readthedocs.io/) tool.

```bash
black .
```

### Documentation

XRLint documentation is built using the [mkdocs](https://www.mkdocs.org/) tool.

With repository root as current working directory:

```bash
pip install .[doc]

mkdocs build
mkdocs serve
mkdocs gh-deploy
```

## License

XRLint is open source made available under the terms and conditions of the 
[MIT License](https://github.com/bcdev/xrlint/blob/main/LICENSE).

Copyright © 2025 Brockmann Consult Development
