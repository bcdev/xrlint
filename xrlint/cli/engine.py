import click
import fsspec

from xrlint.cli.config import read_config
from xrlint.cli.constants import CONFIG_DEFAULT_FILENAMES
from xrlint.cli.constants import DEFAULT_OUTPUT_FORMAT
from xrlint.config import ConfigList
from xrlint.config import get_base_config
from xrlint.formatter import FormatterContext
from xrlint.formatters import export_formatters
from xrlint.linter import Linter
from xrlint.result import Message
from xrlint.result import Result


class CliEngine:

    # noinspection PyShadowingBuiltins
    def __init__(
        self,
        no_default_config: int = False,
        config_path: str | None = None,
        output_format: str = DEFAULT_OUTPUT_FORMAT,
        output_path: str | None = None,
        files: list[str] | None = None,
        recommended: bool = True,
    ):
        self.no_default_config = no_default_config
        self.config_path = config_path
        self.output_format = output_format
        self.output_path = output_path
        self.files = files
        self.base_config = get_base_config(recommended=recommended)
        self.config_list = ConfigList([self.base_config])

    def load_config(self) -> None:
        config_list = None

        if self.config_path:
            try:
                config_list = read_config(config_path=self.config_path)
            except FileNotFoundError:
                raise click.ClickException(f"{self.config_path}: file not found")
        elif not self.no_default_config:
            for f in CONFIG_DEFAULT_FILENAMES:
                try:
                    config_list = read_config(config_path=f)
                except FileNotFoundError:
                    pass

        if config_list is not None:
            self.config_list = ConfigList([self.base_config] + config_list.configs)

    def verify_datasets(self) -> list[Result]:
        results: list[Result] = []
        for file_path in self.files:
            config = self.config_list.compute_config(file_path)
            if config is not None:
                # TODO: use config.processor
                linter = Linter(config=config)
                result = linter.verify_dataset(file_path)
            else:
                result = Result.new(
                    config,
                    file_path,
                    [Message(message="No configuration matches this file", severity=2)],
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
