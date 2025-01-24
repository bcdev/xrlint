import json
import os
from collections.abc import Iterable, Iterator

import click
import fsspec
import yaml

from xrlint.cli.config import ConfigError, read_config_list
from xrlint.cli.constants import (
    DEFAULT_CONFIG_FILE_YAML,
    DEFAULT_CONFIG_FILES,
    DEFAULT_GLOBAL_FILES,
    DEFAULT_GLOBAL_IGNORES,
    DEFAULT_MAX_WARNINGS,
    DEFAULT_OUTPUT_FORMAT,
    INIT_CONFIG_YAML,
)
from xrlint.config import Config, ConfigList, get_core_config
from xrlint.formatter import FormatterContext
from xrlint.formatters import export_formatters
from xrlint.linter import Linter
from xrlint.plugin import Plugin
from xrlint.result import Result, ResultStats
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
        The function will load the configuration list from a specified
        configuration file, if any.
        Otherwise it will search for the default configuration files
        in the current working directory.
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
            file_path: A file path or URL.

        Returns:
            A configuration object or `None` if no item
                in the configuration list applies.
        """
        return self.config_list.compute_config(file_path)

    def print_config_for_file(self, file_path: str) -> None:
        """Print computed configuration for the given file.

        Args:
            file_path: A file path or URL.
        """
        config = self.get_config_for_file(file_path)
        config_json_obj = config.to_json() if config is not None else None
        click.echo(json.dumps(config_json_obj, indent=2))

    def verify_datasets(self, files: Iterable[str]) -> Iterator[Result]:
        """Verify given files or directories which may also be given as URLs.
        The function produces a validation result for each file.

        Args:
            files: Iterable of files.

        Returns:
            Iterator of reports.
        """
        linter = Linter()
        for file_path, config in self.get_files(files):
            yield linter.verify_dataset(file_path, config=config)

    def get_files(self, file_paths: Iterable[str]) -> Iterator[tuple[str, Config]]:
        """Provide an iterator for the list of files or directories.

        Directories in `files` that are not filtered out will be
        recursively traversed.

        Args:
            file_paths: Iterable of files or directory.

        Returns:
            An iterator of filtered files or directories.
        """
        config_list, global_filter = self.config_list.split_global_filter(
            default=DEFAULT_GLOBAL_FILTER
        )

        def compute_config(p: str):
            return config_list.compute_config(p) if global_filter.accept(p) else None

        for file_path in file_paths:
            _fs, root = fsspec.url_to_fs(file_path)
            fs: fsspec.AbstractFileSystem = _fs

            config = compute_config(file_path)
            if config is not None:
                yield file_path, config
                continue

            if fs.isdir(root):
                for path, dirs, files in fs.walk(root, topdown=True):
                    for d in list(dirs):
                        d_path = f"{path}/{d}"
                        c = compute_config(d_path)
                        if c is not None:
                            dirs.remove(d)
                            yield d_path, c

                    for f in files:
                        f_path = f"{path}/{f}"
                        c = compute_config(f_path)
                        if c is not None:
                            yield f_path, c

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
