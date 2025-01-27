from typing import Any

import xarray as xr

from xrlint.config import Config
from xrlint.result import Message, Result

from ..constants import NODE_ROOT_NAME
from .apply import apply_rule
from .rulectx import RuleContextImpl


def verify_dataset(config: Config, dataset: Any, file_path: str):
    assert isinstance(config, Config)
    assert dataset is not None
    assert isinstance(file_path, str)
    if isinstance(dataset, xr.Dataset):
        messages = _verify_dataset(config, dataset, file_path, None)
    else:
        messages = _open_and_verify_dataset(config, dataset, file_path)
    return Result.new(config=config, messages=messages, file_path=file_path)


def _verify_dataset(
    config: Config,
    dataset: xr.Dataset,
    file_path: str,
    file_index: int | None,
) -> list[Message]:
    assert isinstance(config, Config)
    assert isinstance(dataset, xr.Dataset)
    assert isinstance(file_path, str)

    if not config.rules:
        return [new_fatal_message("No rules configured or applicable.")]

    context = RuleContextImpl(config, dataset, file_path, file_index)
    for rule_id, rule_config in config.rules.items():
        with context.use_state(rule_id=rule_id):
            apply_rule(context, rule_id, rule_config)
    return context.messages


def _open_and_verify_dataset(
    config: Config, ds_source: Any, file_path: str
) -> list[Message]:
    assert isinstance(config, Config)
    assert ds_source is not None
    assert isinstance(file_path, str)

    opener_options = config.opener_options or {}
    if config.processor is not None:
        processor_op = config.get_processor_op(config.processor)
        try:
            ds_path_list = processor_op.preprocess(file_path, opener_options)
        except (OSError, ValueError, TypeError) as e:
            return [new_fatal_message(str(e))]
        return processor_op.postprocess(
            [
                _verify_dataset(config, ds, path, i)
                for i, (ds, path) in enumerate(ds_path_list)
            ],
            file_path,
        )
    else:
        try:
            dataset = _open_dataset(ds_source, opener_options, file_path)
        except (OSError, ValueError, TypeError) as e:
            return [new_fatal_message(str(e))]
        with dataset:
            return _verify_dataset(config, dataset, file_path, None)


def _open_dataset(
    ds_source: Any, opener_options: dict[str, Any] | None, file_path: str
) -> xr.Dataset:
    """Open a dataset."""
    engine = opener_options.pop("engine", None)
    if engine is None and (file_path.endswith(".zarr") or file_path.endswith(".zarr/")):
        engine = "zarr"
    return xr.open_dataset(ds_source, engine=engine, **(opener_options or {}))


def new_fatal_message(message: str) -> Message:
    return Message(
        message=message,
        fatal=True,
        severity=2,
        node_path=NODE_ROOT_NAME,
    )
