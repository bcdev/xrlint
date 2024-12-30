import sys

import click

# Warning: do not import heavy stuff here,
# Option "--help" can be slow otherwise!
from xrlint.version import version
from xrlint.cli.constants import DEFAULT_MAX_WARNINGS
from xrlint.cli.constants import DEFAULT_OUTPUT_FORMAT
from xrlint.cli.constants import CONFIG_DEFAULT_BASENAME


@click.command(name="xrlint")
@click.option(
    f"--no-default-config",
    "no_default_config",
    help=f"Disable use of default configuration from {CONFIG_DEFAULT_BASENAME}.*",
    is_flag=True,
)
@click.option(
    "--config",
    "-c",
    "config_path",
    help=(
        f"Use this configuration, overriding {CONFIG_DEFAULT_BASENAME}.*"
        f" config options if present"
    ),
    metavar="PATH",
)
@click.option(
    "-f",
    "--format",
    "output_format",
    help=f"Use a specific output format - default: {DEFAULT_OUTPUT_FORMAT}",
    default=DEFAULT_OUTPUT_FORMAT,
    metavar="NAME",
)
@click.option(
    "--max-warnings",
    "max_warnings",
    help=(
        f"Number of warnings to trigger nonzero exit code"
        f" - default: {DEFAULT_MAX_WARNINGS})"
    ),
    type=int,
    default=DEFAULT_MAX_WARNINGS,
    metavar="COUNT",
)
@click.argument("files", nargs=-1)
@click.version_option(version)
@click.help_option()
def main(
    no_default_config: bool,
    config_path: str | None,
    max_warnings: int,
    output_format: str,
    files: list[str] | None,
):
    """Lint the given FILES."""
    from xrlint.cli.engine import CliEngine

    cli_engine = CliEngine(
        no_default_config=no_default_config,
        config_path=config_path,
        files=files,
        output_format=output_format,
    )

    cli_engine.load_config()
    results = cli_engine.verify_datasets()
    output_text = cli_engine.format_results(results)
    print(output_text)

    errors = sum(r.error_count for r in results)
    warnings = sum(r.warning_count for r in results)
    return 1 if errors > 0 or warnings > max_warnings else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
