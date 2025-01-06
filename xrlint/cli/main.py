import sys

import click

# Warning: do not import heavy stuff here, it can
# slow down commands like "xrlint --help" otherwise.
from xrlint.version import version
from xrlint.cli.constants import (
    DEFAULT_MAX_WARNINGS,
    DEFAULT_OUTPUT_FORMAT,
    DEFAULT_CONFIG_BASENAME,
)


@click.command(name="xrlint")
@click.option(
    "--no-default-config",
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
        "Specify plugins. MODULE is the name of Python module"
        " that defines an 'export_plugin()' function."
    ),
    metavar="MODULE",
    multiple=True,
)
@click.option(
    "--rule",
    "rule_specs",
    help=(
        "Specify rules. SPEC must have format"
        " '<rule-name>: <rule-config>' (note the space character)."
    ),
    metavar="SPEC",
    multiple=True,
)
@click.option(
    "-o",
    "--output-file",
    "output_file",
    help="Specify file to write report to",
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
    "--color/--no-color",
    "color_enabled",
    default=True,
    help="Force enabling/disabling of color",
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
@click.option(
    "--init",
    "init_mode",
    help="Write initial configuration file and exit.",
    is_flag=True,
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
    output_file: str | None,
    output_format: str,
    color_enabled: bool,
    init_mode: bool,
    files: tuple[str, ...],
):
    """Validate the given dataset FILES.

    Reads configuration from `xrlint.config.*` if file exists and
    unless `--no-default-config` is set or `--config PATH` is provided.
    Then validates each dataset in FILES against the configuration.
    The validation result is dumped to standard output if not otherwise
    stated by `--output-file PATH`. The output format is `simple`. Other
    inbuilt formats are `json` and `html` which can by setting the
    `--format NAME` option.
    """
    from xrlint.cli.engine import CliEngine

    if init_mode:
        CliEngine.init_config_file()
        raise click.exceptions.Exit(0)

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
        color_enabled=color_enabled,
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
