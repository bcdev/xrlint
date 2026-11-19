# Pixi handover

[Issue #80](https://github.com/bcdev/xrlint/issues/80) · Branch `forman/80-use_pixi`

Pixi is configured in [pyproject.toml](pyproject.toml) with Python 3.14 for local development and locked Python 3.10–3.13 environments for GitHub Actions. The contributor docs and both workflows use Pixi. The old `environment.yml` and its references were removed.

```sh
pixi install
pixi run format
pixi run checks
pixi run tests
```

CI runs `format --check` first and still uploads coverage to Codecov. All 443 tests passed on Windows for each CI Python version. Workflow validation, the strict MkDocs build, and the wheel and source builds also passed locally.

## Continue here

- Review and stage the changes, including the latest `pixi.lock` updates, which are still unstaged. Verify the Linux CI run on GitHub after pushing the branch.
- Missing named tasks are `docs-build` for `mkdocs build --strict`, `docs-serve` for `mkdocs serve`, and `build` for `python -m build`. The MkDocs tasks would need the `doc` extra in a Pixi environment. The release workflow already runs `python -m build` through Pixi.
