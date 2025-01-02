from os import PathLike
from pathlib import Path
from typing import Any

import click
import fsspec

from xrlint.config import ConfigList
from xrlint.util.formatting import format_message_type_of
from xrlint.util.importutil import eval_exported_value


def read_config(config_path: str | Path | PathLike[str]) -> ConfigList:
    if not isinstance(config_path, (str, Path, PathLike)):
        raise TypeError(
            format_message_type_of("config_path", config_path, "str|Path|PathLike")
        )

    try:
        config_like = _read_config_like(str(config_path))
    except FileNotFoundError:
        raise
    except (OSError, ValueError, TypeError) as e:
        raise click.ClickException(f"{config_path}: {e}") from e

    try:
        return ConfigList.from_value(config_like)
    except (ValueError, TypeError) as e:
        raise click.ClickException(f"{config_path}: {e}") from e


def _read_config_like(config_path: str) -> Any:
    if config_path.endswith(".yml") or config_path.endswith(".yaml"):
        return _read_config_yaml(config_path)
    if config_path.endswith(".json"):
        return _read_config_json(config_path)
    if config_path.endswith(".py"):
        return _read_config_python(config_path)
    raise ValueError("unsupported configuration file format")


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

    export_function_name = "export_configs"
    _locals = {}
    exec(code, None, _locals)

    try:
        export_function = _locals[export_function_name]
    except KeyError:
        raise ValueError(f"missing definition of function {export_function_name!r}")

    return eval_exported_value(
        export_function_name, export_function, ConfigList.from_value
    )
