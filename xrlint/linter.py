from pathlib import Path
from typing import Any

import xarray as xr

from xrlint.config import Config
from xrlint.config import get_core_config
from xrlint.config import merge_configs
from xrlint.constants import MISSING_DATASET_FILE_PATH
from xrlint.result import Result
from xrlint.rule import RuleConfig
from xrlint.rule import RuleOp

# noinspection PyProtectedMember
from xrlint._linter.rule_ctx_impl import RuleContextImpl

# noinspection PyProtectedMember
from xrlint._linter.verify_impl import verify_dataset


def new_linter(
    recommended: bool = False,
    config: Config | dict | None = None,
    **config_kwargs: dict[str, Any],
) -> "Linter":
    """Create a new `Linter`.

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

    You should not use the constructor directly.
    Instead, use the `new_linter()` function.

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
        dataset: str | Path | xr.Dataset,
        *,
        file_path: str | None = None,
        config: Config | dict[str, Any] | None = None,
        **config_kwargs: dict[str, Any],
    ) -> Result:
        """Verify a dataset.

        Args:
            dataset: The dataset. Can be a `xr.Dataset` instance
                or a file path from which the dataset will be opened.
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

        error: Exception | None = None
        if not isinstance(dataset, xr.Dataset):
            ds_source = dataset
            dataset, error = open_dataset(ds_source, config.opener_options or {})
            if not file_path and isinstance(ds_source, (str, Path)):
                file_path = str(ds_source)

        if dataset is not None and not file_path:
            file_path = _get_file_path_for_dataset(dataset)

        context = RuleContextImpl(config=config, dataset=dataset, file_path=file_path)

        if error:
            context.report(str(error), fatal=True)
        elif not config.rules:
            context.report("No rules configured or applicable.", fatal=True)
        else:
            # TODO: validate config,
            #   e.g., validate any rule options against rule.meta.schema
            for rule_id, rule_config in config.rules.items():
                with context.use_state(rule_id=rule_id):
                    _apply_rule(context, rule_id, rule_config)

        return Result.new(
            config=config, file_path=context.file_path, messages=context.messages
        )


def open_dataset(
    file_path: str, opener_options: dict[str, Any] | None
) -> tuple[xr.Dataset, None] | tuple[None, Exception]:
    """Open a dataset."""
    engine = opener_options.pop("engine", None)
    if engine is None and file_path.endswith(".zarr"):
        engine = "zarr"

    try:
        return xr.open_dataset(file_path, engine=engine, **(opener_options or {})), None
    except (OSError, TypeError, ValueError) as e:
        return None, e


def _apply_rule(
    context: RuleContextImpl,
    rule_id: str,
    rule_config: RuleConfig,
):
    """Apply rule given by `rule_id` to dataset given by
    `context` using rule configuration `rule_config`.
    """
    try:
        rule = context.config.get_rule(rule_id)
    except ValueError as e:
        context.report(f"{e}", fatal=True)
        return

    if rule_config.severity == 0:
        # rule is off
        return

    with context.use_state(severity=rule_config.severity):
        # noinspection PyArgumentList
        verifier: RuleOp = rule.op_class(*rule_config.args, **rule_config.kwargs)
        verify_dataset(verifier, context)


def _get_file_path_for_dataset(dataset: xr.Dataset) -> str:
    source = dataset.encoding.get("source")
    file_path = source if isinstance(source, str) else ""
    return file_path or MISSING_DATASET_FILE_PATH
