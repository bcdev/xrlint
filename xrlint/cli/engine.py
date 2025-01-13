from collections.abc import Iterable, Iterator
import json
import os

import click
import fsspec
import yaml

from xrlint.cli.config import read_config_list, ConfigError
from xrlint.cli.constants import DEFAULT_CONFIG_FILES
from xrlint.cli.constants import DEFAULT_CONFIG_FILE_YAML
from xrlint.cli.constants import DEFAULT_GLOBAL_FILES
from xrlint.cli.constants import DEFAULT_GLOBAL_IGNORES
from xrlint.cli.constants import DEFAULT_OUTPUT_FORMAT
from xrlint.cli.constants import DEFAULT_MAX_WARNINGS
from xrlint.cli.constants import INIT_CONFIG_YAML
from xrlint.config import Config
from xrlint.config import ConfigList
from xrlint.config import get_core_config
from xrlint.formatter import FormatterContext
from xrlint.formatters import export_formatters
from xrlint.linter import Linter
from xrlint.plugin import Plugin
from xrlint.result import Message
from xrlint.result import Result
from xrlint.result import ResultStats
from xrlint.util.filefilter import FileFilter


DEFAULT_GLOBAL_FILTER = FileFilter.from_patterns(
    DEFAULT_GLOBAL_FILES, DEFAULT_GLOBAL_IGNORES
)


class XRLint(FormatterContext):
    """This class provides the engine behind the XRLint
    CLI application.
    It represents the highest level component in the Python API.
    """

    # noinspection PyShadowingBuiltins
    def __init__(
        self,
        no_config_lookup: int = False,
        config_path: str | None = None,
        plugin_specs: tuple[str, ...] = (),
        rule_specs: tuple[str, ...] = (),
        output_format: str = DEFAULT_OUTPUT_FORMAT,
        output_path: str | None = None,
        output_styled: bool = True,
        max_warnings: int = DEFAULT_MAX_WARNINGS,
    ):
        self.no_config_lookup = no_config_lookup
        self.config_path = config_path
        self.plugin_specs = plugin_specs
        self.rule_specs = rule_specs
        self.output_format = output_format
        self.output_path = output_path
        self.output_styled = output_styled
        self.max_warnings = max_warnings
        self._result_stats = ResultStats()
        self.config_list = ConfigList()

    @property
    def max_warnings_exceeded(self) -> bool:
        """`True` if the maximum number of warnings has been exceeded."""
        return self._result_stats.warning_count > self.max_warnings

    @property
    def result_stats(self) -> ResultStats:
        """Get current result statistics."""
        return self._result_stats

    def load_config_list(self) -> None:
        """Load configuration list.
        The function considers any `plugin` and `rule`
        options, the default configuration file names or a specified
        configuration file.
        """
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
        elif not self.no_config_lookup:
            for config_path in DEFAULT_CONFIG_FILES:
                try:
                    config_list = read_config_list(config_path)
                    break
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

        self.config_list = ConfigList.from_value(configs)

    def get_config_for_file(self, file_path: str) -> Config | None:
        """Compute configuration for the given file.

        Args:
            file_path: A file path.

        Returns:
            A configuration object or `None` if no item
                in the configuration list applies.
        """
        return self.config_list.compute_config(file_path)

    def print_config_for_file(self, file_path: str) -> None:
        """Print computed configuration for the given file.

        Args:
            file_path: A file path.
        """
        config = self.get_config_for_file(file_path)
        config_json_obj = config.to_json() if config is not None else None
        click.echo(json.dumps(config_json_obj, indent=2))

    def verify_datasets(self, files: Iterable[str]) -> Iterator[Result]:
        """Verify given files.
        The function produces a validation result for each file.

        Args:
            files: Iterable of files.

        Returns:
            Iterator of reports.
        """
        global_filter = self.config_list.get_global_filter(
            default=DEFAULT_GLOBAL_FILTER
        )
        linter = Linter()
        for file_path, is_dir in get_files(files, global_filter):
            config = self.get_config_for_file(file_path)
            if config is not None:
                yield linter.verify_dataset(file_path, config=config)
            else:
                yield Result.new(
                    config=config,
                    file_path=file_path,
                    messages=[
                        Message(
                            message="No configuration matches this file.",
                            severity=2,
                        )
                    ],
                )

    def format_results(self, results: Iterable[Result]) -> str:
        """Format the given results.

        Args:
            results: Iterable of results.

        Returns:
            A report in plain text.
        """
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
        # TODO: pass and validate format-specific args/kwargs
        #   against formatter.meta.schema
        if output_format == "simple":
            formatter_kwargs = {
                "styled": self.output_styled and self.output_path is None,
                "output": self.output_path is None,
            }
        else:
            formatter_kwargs = {}
        # noinspection PyArgumentList
        formatter_op = formatter.op_class(**formatter_kwargs)
        return formatter_op.format(self, self._result_stats.collect(results))

    def write_report(self, report: str) -> None:
        """Write the validation report provided as plain text."""
        if self.output_path:
            with fsspec.open(self.output_path, mode="w") as f:
                f.write(report)
        elif self.output_format != "simple":
            # The simple formatters outputs incrementally to console
            print(report)

    @classmethod
    def init_config_file(cls) -> None:
        """Write an initial configuration file.
        The file is written into the current working directory.
        """
        file_path = DEFAULT_CONFIG_FILE_YAML
        if os.path.exists(file_path):
            raise click.ClickException(f"file {file_path} already exists.")
        with open(file_path, "w") as f:
            f.write(INIT_CONFIG_YAML)
        click.echo(f"Configuration template written to {file_path}")


def get_files(
    file_paths: Iterable[str], global_filter: FileFilter
) -> Iterator[tuple[str, bool | None]]:
    """Provide an iterator for the list of files or directories.

    Directories in `files` that are not filtered out will be
    recursively traversed.

    Args:
        file_paths: Iterable of files or directory.
        global_filter: A file filter that includes files that
            covered by global file patterns and not excluded
            by global ignore patterns.

    Returns:
        An iterator of filtered files or directories.
    """
    for file_path in file_paths:
        _fs, root = fsspec.url_to_fs(file_path)
        fs: fsspec.AbstractFileSystem = _fs
        _dir = fs.isdir(root)
        if global_filter.accept(file_path):
            yield file_path, _dir
        elif _dir:
            for path, dirs, files in fs.walk(root):
                for d in dirs:
                    d_path = f"{path}/{d}"
                    if global_filter.accept(d_path):
                        yield d_path, True
                for f in files:
                    f_path = f"{path}/{f}"
                    if global_filter.accept(f_path):
                        yield f_path, False
