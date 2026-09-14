# Development Notes

This page records limitations and possible future work. It is not a release
schedule or a list of features currently supported.

## Current limitations

- Rule argument schemas are published as metadata but are not validated before
  rule construction. See the TODO in `xrlint/_linter/apply.py`.
- Automatic dataset fixes are not implemented. Suggestions are available in
  result messages, but there is no CLI option for applying them.
- The only built-in report formats are `simple`, `json`, and `html`.
  Formatter-specific constructor options cannot currently be configured by CLI.
- `linter_options` is reserved and has no operational effect.
- CLI filesystem discovery does not receive dataset `opener_options`.
  Anonymous or specially configured remote listing requires a separately
  configured filesystem.
- Tree traversal validates dataset contents at leaves. Dataset contents on
  non-leaf groups are not independently traversed, although the core
  `conventions` and `content-desc` rules can read parent metadata.
- In 0.6.0, `acdd/acdd_1.1` references unregistered rules, and
  `acdd/acdd_1.3_strict_recommended` contains an invalid unprefixed rule name.
  See the [preset limitations and override](config.md#predefined-configuration-objects).

## Potential improvements

- Validate rule arguments against schemas before execution.
- Add dedicated, consistent presentation of suggestions in console and notebook
  reports.
- Support automatic fixes and Markdown reports.
- Expose formatter arguments and validate them against formatter schemas.
- Improve chunking diagnostics and add focused rules where useful.
- Add documentation URLs for rules that currently lack them.
- Add a project logo.

## Design ideas

A future opener abstraction could separate source selection and opening from
rule execution. Today, custom [processors](config.md#custom-processors) provide
the extension point for alternate dataset layouts.

Additional plugins could cover structured and unstructured grid conventions.

Supporting data models beyond xarray would require explicit decisions about
opening, node types, traversal, and rule compatibility. The current rule
callbacks use a visitor-style traversal over xarray-specific nodes; a generalized
design would need an equivalent traversal contract for each supported model.
