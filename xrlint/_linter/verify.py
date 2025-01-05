from os import PathLike
from pathlib import Path
from typing import Any

import xarray as xr

from xrlint.constants import MISSING_DATASET_FILE_PATH
from xrlint.config import Config
from xrlint.result import Message
from xrlint.result import Result
from .rulectx import RuleContextImpl
from .apply import apply_rule


def verify_dataset(config: Config, dataset: Any, file_path: str | None):
    assert isinstance(config, Config)
    assert dataset is not None
    assert isinstance(file_path, (str, type(None)))
    if isinstance(dataset, xr.Dataset):
        file_path = file_path or _get_file_path_for_dataset(dataset)
        messages = _verify_dataset(config, dataset, file_path)
    else:
        file_path = file_path or _get_file_path_for_source(dataset)
        messages = _open_and_verify_dataset(config, dataset, file_path)
    return Result.new(config=config, messages=messages, file_path=file_path)


def _verify_dataset(
    config: Config,
    dataset: xr.Dataset,
    file_path: str,
) -> list[Message]:
    assert isinstance(config, Config)
    assert isinstance(dataset, xr.Dataset)
    assert isinstance(file_path, str)

    context = RuleContextImpl(config, dataset, file_path)

    if not config.rules:
        context.report("No rules configured or applicable.", fatal=True)
    else:
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
            return [Message(message=str(e), fatal=True, severity=2)]
        return processor_op.postprocess(
            [_verify_dataset(config, ds, path) for ds, path in ds_path_list],
            file_path,
        )
    else:
        try:
            dataset = _open_dataset(ds_source, opener_options, file_path)
        except (OSError, ValueError, TypeError) as e:
            return [Message(message=str(e), fatal=True, severity=2)]
        with dataset:
            return _verify_dataset(config, dataset, file_path)


def _open_dataset(
    ds_source: Any, opener_options: dict[str, Any] | None, file_path: str
) -> xr.Dataset:
    """Open a dataset."""
    engine = opener_options.pop("engine", None)
    if engine is None and (file_path.endswith(".zarr") or file_path.endswith(".zarr/")):
        engine = "zarr"
    return xr.open_dataset(ds_source, engine=engine, **(opener_options or {}))


def _get_file_path_for_dataset(dataset: xr.Dataset) -> str:
    ds_source = dataset.encoding.get("source")
    return _get_file_path_for_source(ds_source)


def _get_file_path_for_source(ds_source: Any) -> str:
    file_path = str(ds_source) if isinstance(ds_source, (str, Path, PathLike)) else ""
    return file_path or MISSING_DATASET_FILE_PATH
