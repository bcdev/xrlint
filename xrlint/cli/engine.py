import click

from xrlint.cli.config import read_config
from xrlint.cli.constants import DEFAULT_CONFIG_FILENAMES
from xrlint.cli.constants import DEFAULT_OUTPUT_FORMAT
from xrlint.config import Config
from xrlint.config import EffectiveConfig
from xrlint.formatter import FormatterContext
from xrlint.formatters import import_formatters
from xrlint.linter import Linter
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
        self.config = EffectiveConfig(common=Config())

        self.rule_registry = import_rules()
        self.formatter_registry = import_formatters()

    def load_config(self):
        if self.config is not None:
            return

        config = EffectiveConfig(common=Config())

        if self.config_path:
            try:
                c = read_config(config_path=self.config_path)
                config = config.merge(c)
            except FileNotFoundError:
                raise click.ClickException(f"File not found: {self.config_path}")
        elif not self.no_default_config:
            for f in DEFAULT_CONFIG_FILENAMES:
                try:
                    c = read_config(config_path=f)
                    config = config.merge(c)
                except FileNotFoundError:
                    pass

        self.config = EffectiveConfig.from_value(config)

    def verify_datasets(self) -> list[Result]:
        results: list[Result] = []
        for file_path in self.files:
            config = self.config.resolve_for_path(file_path)
            if config is not None:
                linter = Linter(config=config, _registry=self.rule_registry)
                result = linter.verify_dataset(file_path)
                results.append(result)
        return results

    def format_results(self, results: list[Result]) -> str:
        output_format = (
            self.output_format if self.output_format else DEFAULT_OUTPUT_FORMAT
        )
        formatter = self.formatter_registry.lookup(output_format)
        if formatter is None:
            raise click.ClickException(f"unknown format {output_format!r}")
        # TODO: pass format-specific args/kwargs
        return formatter.op_class().format(FormatterContext(False), results)
