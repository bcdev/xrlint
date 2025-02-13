#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from os import PathLike
from pathlib import Path
from typing import Any

import xarray as xr

from xrlint.config import Config, ConfigLike, get_core_config_object
from xrlint.result import Result

from ._linter.validate import new_fatal_message, validate_dataset
from .constants import MISSING_DATASET_FILE_PATH, MISSING_DATATREE_FILE_PATH


def new_linter(*configs: ConfigLike, **config_props: Any) -> "Linter":
    """Create a new `Linter` with the core plugin included and the
     given additional configuration.

    Args:
        *configs: Variable number of configuration-like arguments.
            For more information see the
            [ConfigLike][xrlint.config.ConfigLike] type alias.
        **config_props: Individual configuration object properties.
            For more information refer to the properties of a
            [ConfigObject][xrlint.config.ConfigObject].

    Returns:
        A new linter instance
    """
    return Linter(get_core_config_object(), *configs, **config_props)


class Linter:
    """The linter.

    Using the constructor directly creates an empty linter
    with no configuration - even without the core plugin and
    its predefined rule configurations.
    If you want a linter with core plugin included use the
    `new_linter()` function.

    Args:
        *configs: Variable number of configuration-like arguments.
            For more information see the
            [ConfigLike][xrlint.config.ConfigLike] type alias.
        **config_props: Individual configuration object properties.
            For more information refer to the properties of a
            [ConfigObject][xrlint.config.ConfigObject].
    """

    def __init__(self, *configs: ConfigLike, **config_props: Any):
        self._config = Config.from_config(*configs, config_props)

    @property
    def config(self) -> Config:
        """Get this linter's configuration."""
        return self._config

    def validate(
        self,
        dataset: Any,
        *,
        file_path: str | None = None,
        config: ConfigLike = None,
        **config_props: Any,
    ) -> Result:
        """Validate a dataset against applicable rules.

        Args:
            dataset: The dataset. Can be a `xr.Dataset` or `xr.DataTree`
                instance or a file path, or any dataset source that can
                be opened using `xarray.open_dataset()`
                or `xarray.open_datatree()`.
            file_path: Optional file path used for formatting
                messages. Useful if `dataset` is not a file path.
            config: Optional configuration-like value.
                For more information see the
                [ConfigLike][xrlint.config.ConfigLike] type alias.
            **config_props: Individual configuration object properties.
                For more information refer to the properties of a
                [ConfigObject][xrlint.config.ConfigObject].

        Returns:
            Result of the validation.
        """
        if not file_path:
            if isinstance(dataset, (xr.Dataset, xr.DataTree)):
                file_path = file_path or _get_file_path_for_dataset(dataset)
            else:
                file_path = file_path or _get_file_path_for_source(dataset)

        config = Config.from_config(self._config, config, config_props)
        config_obj = config.compute_config_object(file_path)
        if config_obj is None or not config_obj.rules:
            return Result(
                file_path=file_path,
                messages=[
                    new_fatal_message(
                        f"No configuration given or matches {file_path!r}.",
                    )
                ],
            )

        return validate_dataset(config_obj, dataset, file_path)


def _get_file_path_for_dataset(dataset: xr.Dataset | xr.DataTree) -> str:
    ds_source = dataset.encoding.get("source")
    return _get_file_path_for_source(
        ds_source,
        MISSING_DATASET_FILE_PATH
        if isinstance(dataset, xr.Dataset)
        else MISSING_DATATREE_FILE_PATH,
    )


def _get_file_path_for_source(ds_source: Any, default: str | None = None) -> str:
    file_path = str(ds_source) if isinstance(ds_source, (str, Path, PathLike)) else ""
    return file_path or (default or MISSING_DATASET_FILE_PATH)
