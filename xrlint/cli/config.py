from os import PathLike
from pathlib import Path
from typing import Any

import fsspec

from xrlint.config import ConfigList
from xrlint.util.formatting import format_message_type_of
from xrlint.util.importutil import eval_exported_value


def read_config(config_path: str | Path | PathLike[str]) -> ConfigList:
    if not isinstance(config_path, (str, Path, PathLike)):
        raise TypeError(
            format_message_type_of(
                "configuration file", config_path, "str|Path|PathLike"
            )
        )

    if config_path.endswith(".yml") or config_path.endswith(".yaml"):
        config_like = _read_config_yaml(config_path)
    elif config_path.endswith(".json"):
        config_like = _read_config_json(config_path)
    elif config_path.endswith(".py"):
        config_like = _read_config_python(config_path)
    else:
        raise ValueError(f"unsupported configuration file format: {config_path}")

    try:
        return ConfigList.from_value(config_like)
    except (ValueError, TypeError) as e:
        raise type(e)(f"configuration in {config_path}: {e}") from e


def _read_config_yaml(config_path) -> Any:
    import yaml

    with fsspec.open(config_path, mode="r") as f:
        return yaml.load(f, Loader=yaml.SafeLoader)


def _read_config_json(config_path) -> Any:
    import json

    with fsspec.open(config_path, mode="r") as f:
        return json.load(f)


def _read_config_python(config_path) -> Any:
    import fsspec

    with fsspec.open(config_path, mode="r") as f:
        code = f.read()

    export_function_name = "export_config"
    _locals = {}
    exec(code, None, _locals)

    try:
        export_function = _locals[export_function_name]
    except KeyError:
        raise AttributeError(f"missing attribute {export_function_name!r}")

    return eval_exported_value(
        export_function_name, export_function, ConfigList.from_value
    )
