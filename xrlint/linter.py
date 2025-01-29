from os import PathLike
from pathlib import Path
from typing import Any

import xarray as xr

from xrlint.config import Config, get_core_config_object, ConfigLike
from xrlint.result import Result

from ._linter.verify import new_fatal_message, verify_dataset
from .constants import MISSING_DATASET_FILE_PATH


def new_linter(*configs: ConfigLike, **config_kwargs: Any) -> "Linter":
    """Create a new `Linter` with the given configuration.

    Args:
        configs: Variable arguments comprising configuration,
            or configuration objects, or lists of configuration objects
            or named configurations.
            Use `"recommended"` if the recommended configuration
            of the builtin rules should be used, or `"all"` if all rules
            shall be used.
        config_kwargs: Individual [Config][xrlint.config.Config] properties
            of an additional configuration object.

    Returns:
        A new linter instance
    """
    return Linter(get_core_config_object(), *configs, **config_kwargs)


class Linter:
    """The linter.

    Using the constructor directly creates an empty linter
    with no configuration - even without default rules loaded.
    If you want a linter with core rules loaded
    use the `new_linter()` function.

    Args:
        configs: Variable arguments comprising configuration,
            or configuration objects, or lists of configuration objects
            or named configurations.
            Use `"recommended"` if the recommended configuration
            of the builtin rules should be used, or `"all"` if all rules
            shall be used.
        config_kwargs: Individual [Config][xrlint.config.Config] properties
            of an additional configuration object.
    """

    def __init__(self, *configs: ConfigLike, **config_kwargs: Any):
        self._config = Config.from_config(*configs, config_kwargs)

    @property
    def config(self) -> Config:
        """Get this linter's configuration."""
        return self._config

    def verify_dataset(
        self,
        dataset: Any,
        *,
        file_path: str | None = None,
        config: ConfigLike = None,
        **config_kwargs: Any,
    ) -> Result:
        """Verify a dataset.

        Args:
            dataset: The dataset. Can be a `xr.Dataset` instance
                or a file path, or any dataset source that can be opened
                using `xarray.open_dataset()`.
            file_path: Optional file path used for formatting
                messages. Useful if `dataset` is not a file path.
            config: Optional configuration, or configuration object,
                or a list of configuration objects that will be added to
                the current linter configuration.
            config_kwargs: Individual [Config][xrlint.config.Config] properties
                of an additional configuration object.

        Returns:
            Result of the verification.
        """
        if not file_path:
            if isinstance(dataset, xr.Dataset):
                file_path = file_path or _get_file_path_for_dataset(dataset)
            else:
                file_path = file_path or _get_file_path_for_source(dataset)

        config = Config.from_config(self._config, config, config_kwargs)
        config_obj = config.compute_config_object(file_path)
        if config_obj is None:
            return Result.new(
                config_object=None,
                file_path=file_path,
                messages=[
                    new_fatal_message(
                        f"No configuration given or matches {file_path!r}.",
                    )
                ],
            )

        return verify_dataset(config_obj, dataset, file_path)


def _get_file_path_for_dataset(dataset: xr.Dataset) -> str:
    ds_source = dataset.encoding.get("source")
    return _get_file_path_for_source(ds_source)


def _get_file_path_for_source(ds_source: Any) -> str:
    file_path = str(ds_source) if isinstance(ds_source, (str, Path, PathLike)) else ""
    return file_path or MISSING_DATASET_FILE_PATH
