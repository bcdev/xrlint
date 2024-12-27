import click

from xrlint.cli.config import read_config
from xrlint.cli.constants import CONFIG_DEFAULT_FILENAMES
from xrlint.cli.constants import DEFAULT_OUTPUT_FORMAT
from xrlint.config import Config
from xrlint.config import ConfigList
from xrlint.formatter import FormatterContext
from xrlint.formatters import import_formatters
from xrlint.linter import Linter
from xrlint.message import Message
from xrlint.plugin import Plugin, PluginMeta
from xrlint.result import Result
from xrlint.rules import import_rules


class CliEngine:

    # noinspection PyShadowingBuiltins
    def __init__(
        self,
        no_default_config: int = False,
        config_path: str | None = None,
        output_format: str = DEFAULT_OUTPUT_FORMAT,
        files: list[str] | None = None,
    ):
        self.no_default_config = no_default_config
        self.config_path = config_path
        self.output_format = output_format
        self.files = files
        self.core_config = Config(
            plugins={
                "core": Plugin(
                    meta=PluginMeta(name="core"), rules=import_rules().as_dict()
                ),
            }
        )
        self.config_list = ConfigList([self.core_config])

    def load_config(self):
        config_list = None

        if self.config_path:
            try:
                config_list = read_config(config_path=self.config_path)
            except FileNotFoundError:
                raise click.ClickException(f"File not found: {self.config_path}")
        elif not self.no_default_config:
            for f in CONFIG_DEFAULT_FILENAMES:
                try:
                    config_list = read_config(config_path=f)
                except FileNotFoundError:
                    pass

        if config_list is not None:
            self.config_list = ConfigList([self.core_config] + config_list.configs)

    def verify_datasets(self) -> list[Result]:
        results: list[Result] = []
        for file_path in self.files:
            config = self.config_list.resolve_for_path(file_path)
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
                            message="No configuration matches this file", severity=2
                        )
                    ],
                )
            results.append(result)

        return results

    def format_results(self, results: list[Result]) -> str:
        output_format = (
            self.output_format if self.output_format else DEFAULT_OUTPUT_FORMAT
        )
        formatter = import_formatters().lookup(output_format)
        if formatter is None:
            raise click.ClickException(f"unknown format {output_format!r}")
        # TODO: pass format-specific args/kwargs
        return formatter.op_class().format(FormatterContext(False), results)
