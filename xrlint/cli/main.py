import sys

import click

# Warning: do not import heavy stuff here,
# Option "--help" can be slow otherwise!
from xrlint.version import version
from xrlint.cli.constants import DEFAULT_MAX_WARNINGS
from xrlint.cli.constants import DEFAULT_OUTPUT_FORMAT
from xrlint.cli.constants import DEFAULT_CONFIG_BASENAME


@click.command(name="xrlint")
@click.option(
    f"--no-default-config",
    "no_default_config",
    help=f"Disable use of default configuration from {DEFAULT_CONFIG_BASENAME}.*",
    is_flag=True,
)
@click.option(
    "--config",
    "-c",
    "config_path",
    help=(
        f"Use this configuration, overriding {DEFAULT_CONFIG_BASENAME}.*"
        f" config options if present"
    ),
    metavar="PATH",
)
@click.option(
    "--plugin",
    "plugin_specs",
    help=(
        f"Specify plugins. MODULE is the name of Python module"
        f" that defines an 'export_plugin()' function."
    ),
    metavar="MODULE",
    multiple=True,
)
@click.option(
    "--rule",
    "rule_specs",
    help=(
        f"Specify rules. SPEC must have format"
        f" '<rule-name>: <rule-config>' (note the space character)."
    ),
    metavar="SPEC",
    multiple=True,
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
    "-o",
    "--output-file",
    "output_file",
    help=f"Specify file to write report to",
    metavar="PATH",
)
@click.option(
    "--max-warnings",
    "max_warnings",
    help=(
        f"Number of warnings to trigger nonzero exit code"
        f" - default: {DEFAULT_MAX_WARNINGS}"
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
    plugin_specs: tuple[str, ...],
    rule_specs: tuple[str, ...],
    max_warnings: int,
    output_format: str,
    output_file: str | None,
    files: tuple[str, ...],
):
    """Lint the given dataset FILES.

    Reads configuration from `./xrlint.config.py` if `--no-default-config`
    is not set and `--config PATH` is not provided, then validates
    each dataset in FILES against the configuration.
    The validation result is dumped to standard output if not otherwise
    stated by `--output-file PATH`. The output format is `simple`. Other
    inbuilt formats are `json` and `html` which can by setting the
    `--format NAME` option.
    """
    from xrlint.cli.engine import CliEngine

    if not files:
        raise click.ClickException("No dataset files provided.")

    cli_engine = CliEngine(
        no_default_config=no_default_config,
        config_path=config_path,
        plugin_specs=plugin_specs,
        rule_specs=rule_specs,
        files=files,
        output_format=output_format,
        output_path=output_file,
    )

    config_list = cli_engine.load_config()
    results = cli_engine.verify_datasets(config_list)
    report = cli_engine.format_results(results)
    cli_engine.write_report(report)

    error_status = sum(r.error_count for r in results) > 0
    max_warn_status = sum(r.warning_count for r in results) > max_warnings
    if max_warn_status and not error_status:
        click.echo("maximum number of warnings exceeded.")
    if max_warn_status or error_status:
        raise click.exceptions.Exit(1)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
