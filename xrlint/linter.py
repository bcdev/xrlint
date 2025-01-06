from typing import Any

from xrlint.config import Config
from xrlint.config import get_core_config
from xrlint.config import merge_configs
from xrlint.result import Result
from ._linter.verify import verify_dataset


def new_linter(
    recommended: bool = False,
    config: Config | dict | None = None,
    **config_kwargs: dict[str, Any],
) -> "Linter":
    """Create a new `Linter` with core rules loaded.

    Args:
        recommended: `True` if the recommended configurations of the builtin
            rules should be used.
            If set to `False` (the default), you should configure the `rules`
            option either in `config` or `config_kwargs`. Otherwise, calling
            `verify_dataset()` without any rule configuration will never
            succeed for any given dataset.
        config: The `config` keyword argument passed to the `Linter` class
        config_kwargs: The `config_kwargs` keyword arguments passed to
            the `Linter` class
    Returns:
        A new linter instance
    """
    return Linter(
        config=merge_configs(get_core_config(recommended=recommended), config),
        **config_kwargs,
    )


class Linter:
    """The linter.

    Using the constructor directly creates an empty linter
    with no configuration - even without default rules loaded.
    If you want a linter with core rules loaded
    use the `new_linter()` function.

    Args:
        config: The linter's configuration.
        config_kwargs: Individual linter configuration options.
            All options of the `Config` object are possible.
            If `config` is given too, provided
            given individual linter configuration options
            merged the ones given in `config`.
    """

    def __init__(
        self,
        config: Config | dict[str, Any] | None = None,
        **config_kwargs: dict[str, Any],
    ):
        self._config = merge_configs(config, config_kwargs)

    @property
    def config(self) -> Config:
        """Get this linter's configuration."""
        return self._config

    def verify_dataset(
        self,
        dataset: Any,
        *,
        file_path: str | None = None,
        config: Config | dict[str, Any] | None = None,
        **config_kwargs: dict[str, Any],
    ) -> Result:
        """Verify a dataset.

        Args:
            dataset: The dataset. Can be a `xr.Dataset` instance
                or a file path, or any dataset source that can be opened
                using `xarray.open_dataset()`.
            file_path: Optional file path used for formatting
                messages. Useful if `dataset` is not a file path.
            config: Configuration tbe merged with the linter's
                configuration.
            config_kwargs: Individual linter configuration options
                to be merged with `config` if any. The merged result
                will be merged with the linter's configuration.
        Returns:
            Result of the verification.
        """
        config = merge_configs(self._config, config)
        config = merge_configs(config, config_kwargs)
        return verify_dataset(config, dataset, file_path)
