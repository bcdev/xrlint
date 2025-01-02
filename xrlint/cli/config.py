import sys
from os import PathLike
from pathlib import Path
from typing import Any

import click
import fsspec

from xrlint.config import ConfigList
from xrlint.util.formatting import format_message_type_of
from xrlint.util.importutil import import_exported_value


def read_config(config_path: str | Path | PathLike[str]) -> ConfigList:
    if not isinstance(config_path, (str, Path, PathLike)):
        raise TypeError(
            format_message_type_of("config_path", config_path, "str|Path|PathLike")
        )

    try:
        config_like = _read_config_like(str(config_path))
    except (FileNotFoundError, ModuleNotFoundError):
        raise
    except (OSError, ValueError, TypeError, AttributeError) as e:
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


def _read_config_python(config_path: str) -> Any:
    module_path = Path(config_path)
    module_parent = module_path.parent
    module_name = module_path.stem

    old_sys_path = sys.path
    sys.path = [module_parent.as_posix()] + sys.path
    try:
        return import_exported_value(module_name, "configs", ConfigList.from_value)
    finally:
        sys.path = old_sys_path
