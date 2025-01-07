# How to contribute

The XRLint project welcomes contributions of any form
as long as you respect our [code of conduct](CODE_OF_CONDUCT.md) and stay 
in line with the following instructions and guidelines.

If you have suggestions, ideas, feature requests, or if you have identified
a malfunction or error, then please 
[post an issue](https://github.com/bcdev/xrlint/issues). 

If you'd like to submit code or documentation changes, we ask you to provide a 
pull request (PR) 
[here](https://github.com/bcdev/xrlint/pulls). 
For code and configuration changes, your PR must be linked to a 
corresponding issue. 

To ensure that your code contributions are consistent with our project’s
coding guidelines, please make sure all applicable items of the following 
checklist are addressed in your PR.  

**PR checklist**

* Format code using [black](https://black.readthedocs.io/) with default settings.
  Check also section [code style](#code-style) below.
* Your change shall not break existing unit tests.
  `pytest` must run without errors.
* Add unit tests for any new code not yet covered by tests.
* Make sure test coverage stays close to 100% for any change.
  Use `pytest --cov=zappend --cov-report=html` to verify.
* If your change affects the current project documentation,
  please adjust it and include the change in the PR.
  Run `mkdocs serve` to verify. 

## Code style

The XRLint code complies to [PEP-8](https://pep8.org/) except for a line 
length of 88 characters as recommended by [black](https://black.readthedocs.io/).
Since black is un-opinionated regarding the order of imports, 
we use the following three import blocks separated by an empty 
line:

1. Python standard library imports, e.g., `os`, `typing`, etc
2. 3rd-party imports, e.g., `xarray`, `zarr`, etc
3. XRLint module imports: 
   Prefer absolute import paths: `from xrlint.a.b.c import d`. 
   Relative imports such as `from .c import d` are ok
   while `..c import d` are not ok.

Use `typing.TYPE_CHECKING` to resolve forward references 
and effectively avoid circular dependencies.

## Contributing Rules

### Rule Naming

The rule naming conventions for XRLint are based ESLint:

* Lower-case only.
* Use dashes between words (kebab-case).
* The rule name should be chosen based on what shall be
  achieved, of what shall be regulated. It names a contract.
* If your rule only disallows something, 
  prefix it with `no-` such as `no-empty-attrs` for disallowing 
  empty attributes in dataset nodes.
* If your rule is enforcing the inclusion of something, 
  use a short name without a special prefix.
* Plugins should add a prefix before their rule names
  separated by a slash, e.g., `xcube/spatial-dims-order`.

### Rule Design

* The reasoning behind a rule should be **easy to grasp**. 

* A rule should serve for a **single purpose only**. Try subdividing
  complex rule logic into multiple rules with simpler logic.

* Each rule should be defined in a dedicated module named after the rule, 
  i.e., `<plugin>/rules/<rule>`. The module name should be the rule's name
  with dashes replaced by underscores. 

* Write a comprehensive test for your rule logic using 
  `xrlint.testing.RuleTester`. It should be defined in a dedicated 
  test module, i.e., `tests/rules/test_<rule>`.
