#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

import time
from typing import Any

import xarray as xr

from xrlint.config import ConfigObject
from xrlint.result import Message, Result

from ..constants import DATASET_ROOT_NAME
from .apply import apply_rule
from .rulectx import RuleContextImpl


def validate_dataset(config_obj: ConfigObject, dataset: Any, file_path: str):
    assert isinstance(config_obj, ConfigObject)
    assert dataset is not None
    assert isinstance(file_path, str)
    if isinstance(dataset, (xr.Dataset, xr.DataTree)):
        messages = _validate_dataset(config_obj, dataset, file_path, None, None)
    else:
        messages = _open_and_validate_dataset(config_obj, dataset, file_path)
    return Result(file_path=file_path, config_object=config_obj, messages=messages)


def _validate_dataset(
    config_obj: ConfigObject,
    dataset: xr.Dataset | xr.DataTree,
    file_path: str,
    file_index: int | None,
    access_latency: float | None,
) -> list[Message]:
    assert isinstance(config_obj, ConfigObject)
    assert isinstance(dataset, (xr.Dataset, xr.DataTree))
    assert isinstance(file_path, str)

    context = RuleContextImpl(
        config_obj, dataset, file_path, file_index, access_latency
    )
    for rule_id, rule_config in config_obj.rules.items():
        with context.use_state(rule_id=rule_id):
            apply_rule(context, rule_id, rule_config)
    return context.messages


def _open_and_validate_dataset(
    config_obj: ConfigObject, ds_source: Any, file_path: str
) -> list[Message]:
    assert isinstance(config_obj, ConfigObject)
    assert ds_source is not None
    assert isinstance(file_path, str)

    opener_options = config_obj.opener_options or {}
    if config_obj.processor is not None:
        processor_op = config_obj.get_processor_op(config_obj.processor)
        t0 = time.time()
        try:
            ds_path_list = processor_op.preprocess(file_path, opener_options)
        except (OSError, ValueError, TypeError) as e:
            return [new_fatal_message(str(e))]
        access_latency = time.time() - t0
        return processor_op.postprocess(
            [
                _validate_dataset(config_obj, ds, path, i, access_latency)
                for i, (ds, path) in enumerate(ds_path_list)
            ],
            file_path,
        )
    else:
        try:
            dataset, access_latency = _open_dataset(
                ds_source, opener_options, file_path
            )
        except (OSError, ValueError, TypeError) as e:
            return [new_fatal_message(str(e))]
        with dataset:
            return _validate_dataset(
                config_obj, dataset, file_path, None, access_latency
            )


def _open_dataset(
    ds_source: Any, opener_options: dict[str, Any] | None, file_path: str
) -> tuple[xr.Dataset | xr.DataTree, float]:
    """Open a dataset."""
    engine = opener_options.pop("engine", None)
    if engine is None and (file_path.endswith(".zarr") or file_path.endswith(".zarr/")):
        engine = "zarr"
    try:
        t0 = time.time()
        result = xr.open_datatree(ds_source, engine=engine, **(opener_options or {}))
        # When opening no-group Zarr datasets we get with xarray 2025.1.2:
        #
        #   File "<...>/site-packages/xarray/backends/zarr.py", line 741, in __init__
        #     self._read_only = self.zarr_group.read_only
        #                       ^^^^^^^^^^^^^^^^^^^^^^^^^
        # AttributeError: 'NoneType' object has no attribute 'read_only'
    except (OSError, ValueError, TypeError, AttributeError):
        t0 = time.time()
        result = xr.open_dataset(ds_source, engine=engine, **(opener_options or {}))
    return result, time.time() - t0


def new_fatal_message(message: str) -> Message:
    return Message(
        message=message,
        fatal=True,
        severity=2,
        node_path=DATASET_ROOT_NAME,
    )
