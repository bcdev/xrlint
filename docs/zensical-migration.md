# Zensical migration notes

Migration and compatibility review date: **2026-11-20**.

The compatibility statements below refer to these project versions, taken from
the lockfiles before and after migration:

| Component | Before migration | After migration |
| --- | --- | --- |
| MkDocs | 1.6.1 | 1.6.1 (transitive API renderer dependency) |
| Material for MkDocs (`mkdocs-material`) | 9.8.2 | Removed |
| Zensical | Not used | 0.0.74 |
| Zensical UI | Not used | 0.0.41 |
| `mkdocs-gen-files` | 0.6.1 | Removed |
| `mkdocstrings` | 1.0.8 | 1.0.8 |
| `mkdocstrings-python` | 2.0.11 | 2.0.11 |
| `mkdocs-autorefs` | 1.4.5 | 1.4.5 (transitive API renderer dependency) |

The documentation uses `zensical.toml` and the classic theme. Build with
`pixi run docs-build` and preview with `pixi run docs-serve`.

Basic functionality is preserved: navigation, light/dark palettes, search,
icons, Markdown extensions, Python API documentation and cross-references,
the custom legal footer, self-hosted Roboto, and the generated rule catalogue.
Pixel-identical rendering and identical search rankings are not migration goals.

## Features implemented outside Zensical

| Previous integration | Replacement | Upstream limitation |
| --- | --- | --- |
| `mkdocs-gen-files` generated the rule catalogue during a build. | `docs/scripts/mkruleref.py` writes `docs/rule-ref.md` before building. The generated file is ignored by Git. | Zensical does not support `gen-files` or arbitrary MkDocs plugins. |
| A MkDocs `on_config` hook downloaded Roboto and its licence. | `docs/scripts/download_fonts.py` prepares the same self-hosted assets before build and preview, reusing downloaded files. | Zensical does not support MkDocs hooks. |
| MkDocs reran the rule generator when Python sources changed. | `docs/scripts/manage.py` polls local rule sources every 0.5 seconds and regenerates in a fresh interpreter. Zensical notices the generated Markdown and reloads the page. | There is no supported build hook for this custom generator. |

Sources: [plugin compatibility](https://zensical.org/docs/compatibility/mkdocs/plugins/)
and [migration guide](https://zensical.org/docs/compatibility/mkdocs/migration/).
Review these before replacing the wrapper with a future Zensical extension API.

## Remaining differences and improvements

- Direct `zensical build` or `zensical serve` commands bypass project preparation.
  Use the Pixi tasks, especially on a clean checkout.
- Preview watches local `xrlint/**/*.py`, `docs/scripts/mkruleref.py`, and
  `pyproject.toml` for rule-reference changes. Installed third-party plugins
  outside this tree are discovered at generation time but are not watched.
  Restart preview after installing plugins or changing external plugin sources.
- Font downloads still need network access on the first run. The downloaded
  fonts and licence are reused for subsequent offline builds. This matches the
  previous behavior; vendoring fonts could remove that first-run dependency.
- Search uses Zensical's native engine rather than MkDocs' Lunr engine. The site
  retains full-text search, but ranking and query behavior can differ. See
  [site search](https://zensical.org/docs/setup/search/).
- Template overrides run under MiniJinja rather than Python Jinja. The current
  footer uses compatible constructs. Future overrides cannot call arbitrary
  Python functions. See [customization](https://zensical.org/docs/customization/).
- Python API pages still use `mkdocstrings-python`. Its dependency chain retains
  MkDocs and `mkdocs-autorefs`, even though Zensical builds and serves the site.
  Removing those transitive dependencies depends on changes in the API renderer.

No current user-facing feature is intentionally removed. The custom generation
and font preparation are maintained here until suitable Zensical extension
support becomes available.

## Migration verification

Verified on 2026-11-20 with Zensical 0.0.74 and the versions listed above:

- The strict documentation build completes without issues.
- All configured navigation pages are generated. API headings and automatic
  cross-references resolve; rule icons render as inline SVG.
- Light/dark controls, the legal footer, social links, CSS, self-hosted fonts,
  and search assets are present in the generated site.
- In a running preview, temporarily editing a rule description updates both
  the generated Markdown and the served rule-reference page. Restoring the
  source updates both again, and stopping the wrapper cleans up the server.
- Focused tests cover rule content, avoiding unnecessary writes, detecting
  source additions/changes/removals, and recovery after a generation error.
