import os

import click
import fsspec
import yaml

from xrlint.cli.config import read_config_list, ConfigError
from xrlint.cli.constants import DEFAULT_CONFIG_FILES
from xrlint.cli.constants import DEFAULT_CONFIG_FILE_YAML
from xrlint.cli.constants import DEFAULT_GLOBAL_FILES
from xrlint.cli.constants import DEFAULT_GLOBAL_IGNORES
from xrlint.cli.constants import INIT_CONFIG_YAML
from xrlint.cli.constants import DEFAULT_OUTPUT_FORMAT
from xrlint.config import ConfigList
from xrlint.config import get_core_config
from xrlint.formatter import FormatterContext
from xrlint.formatters import export_formatters
from xrlint.linter import Linter
from xrlint.plugin import Plugin
from xrlint.result import Message
from xrlint.result import Result
from xrlint.util.filefilter import FileFilter


DEFAULT_GLOBAL_FILTER = FileFilter.from_patterns(
    DEFAULT_GLOBAL_FILES, DEFAULT_GLOBAL_IGNORES
)


class CliEngine:

    # noinspection PyShadowingBuiltins
    def __init__(
        self,
        no_default_config: int = False,
        config_path: str | None = None,
        plugin_specs: tuple[str, ...] = (),
        rule_specs: tuple[str, ...] = (),
        output_format: str = DEFAULT_OUTPUT_FORMAT,
        output_path: str | None = None,
        files: tuple[str, ...] = (),
    ):
        self.no_default_config = no_default_config
        self.config_path = config_path
        self.plugin_specs = plugin_specs
        self.rule_specs = rule_specs
        self.output_format = output_format
        self.output_path = output_path
        self.files = files

    def load_config(self) -> ConfigList:

        plugins = {}
        for plugin_spec in self.plugin_specs:
            plugin = Plugin.from_value(plugin_spec)
            plugins[plugin.meta.name] = plugin

        rules = {}
        for rule_spec in self.rule_specs:
            rule = yaml.load(rule_spec, Loader=yaml.SafeLoader)
            rules.update(rule)

        config_list = None

        if self.config_path:
            try:
                config_list = read_config_list(self.config_path)
            except (FileNotFoundError, ConfigError) as e:
                raise click.ClickException(f"{e}") from e
        elif not self.no_default_config:
            for config_path in DEFAULT_CONFIG_FILES:
                try:
                    config_list = read_config_list(config_path)
                except FileNotFoundError:
                    pass
                except ConfigError as e:
                    raise click.ClickException(f"{e}") from e

        if config_list is None:
            click.echo("Warning: no configuration file found.")

        core_config = get_core_config()
        core_config.plugins.update(plugins)
        configs = [core_config]
        if config_list is not None:
            configs += config_list.configs
        if rules:
            configs += [{"rules": rules}]

        return ConfigList.from_value(configs)

    def verify_datasets(self, config_list: ConfigList) -> list[Result]:
        global_filter = config_list.get_global_filter(default=DEFAULT_GLOBAL_FILTER)
        results: list[Result] = []
        for file_path in self.files:
            if global_filter.accept(file_path):
                config = config_list.compute_config(file_path)
                if config is not None:
                    # TODO: use config.processor
                    linter = Linter(config=config)
                    result = linter.verify_dataset(file_path)
                else:
                    result = Result.new(
                        config=config,
                        file_path=file_path,
                        messages=[
                            Message(
                                message="No configuration matches this file.",
                                severity=2,
                            )
                        ],
                    )
                results.append(result)

        return results

    def format_results(self, results: list[Result]) -> str:
        output_format = (
            self.output_format if self.output_format else DEFAULT_OUTPUT_FORMAT
        )
        formatters = export_formatters()
        formatter = formatters.get(output_format)
        if formatter is None:
            raise click.ClickException(
                f"unknown format {output_format!r}."
                f" The available formats are"
                f" {', '.join(repr(k) for k in formatters.keys())}."
            )
        # TODO: pass format-specific args/kwargs
        return formatter.op_class().format(FormatterContext(False), results)

    def write_report(self, report: str):
        if not self.output_path:
            print(report)
        else:
            with fsspec.open(self.output_path, mode="w") as f:
                f.write(report)

    @classmethod
    def init_config_file(cls):
        file_path = DEFAULT_CONFIG_FILE_YAML
        if os.path.exists(file_path):
            raise click.ClickException(f"{file_path}: file exists.")
        with open(file_path, "w") as f:
            f.write(INIT_CONFIG_YAML)
        click.echo(f"Configuration template written to {file_path}")
