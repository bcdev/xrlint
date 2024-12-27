from os import PathLike
from pathlib import Path
from typing import Any


from xrlint.config import EffectiveConfig
from xrlint.util.formatting import format_message_type_of
from xrlint.util.importutil import import_value


def read_config(config_path: str | Path | PathLike[str]) -> EffectiveConfig:
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

    return EffectiveConfig.from_value(config_like)


def _read_config_yaml(config_path):
    import fsspec
    import yaml

    with fsspec.open(config_path, mode="r") as f:
        return yaml.load(f, Loader=yaml.SafeLoader)


def _read_config_json(config_path):
    import fsspec
    import json

    with fsspec.open(config_path, mode="r") as f:
        return json.load(f)


def _read_config_python(config_path):
    dir_path, module_name, _ext = _split_config_path(config_path)
    return import_value(module_name, attr_name="config", dir_path=dir_path)


def _split_config_path(config_path: Any) -> tuple[str, str, str]:
    text = str(config_path)
    index = text.replace("\\", "/").rfind("/")
    if index >= 0:
        parent, filename = text[:index], text[index + 1]
    else:
        parent, filename = "", text
    basename_and_ext = filename.rsplit(".", maxsplit=1)
    if len(basename_and_ext) == 2:
        basename, ext = basename_and_ext
    else:
        basename, ext = filename, ""
    return parent, basename, ext
