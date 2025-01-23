import itertools
import json
import re
from typing import Any

import fsspec
import xarray as xr

from xrlint.plugins.xcube.constants import (
    ML_FILE_PATTERN,
    ML_META_FILENAME,
)
from xrlint.plugins.xcube.plugin import plugin
from xrlint.plugins.xcube.util import (
    set_dataset_level_info,
    LevelInfo,
    MultiLevelDatasetMeta,
)
from xrlint.processor import ProcessorOp
from xrlint.result import Message

level_pattern = re.compile(r"^(\d+)(?:\.zarr)?$")


@plugin.define_processor("multi-level-dataset")
class MultiLevelDatasetProcessor(ProcessorOp):
    f"""This processor should be used with `files: [{ML_FILE_PATTERN}"]`."""

    def preprocess(
        self, file_path: str, opener_options: dict[str, Any]
    ) -> list[tuple[xr.Dataset, str]]:
        fs, fs_path = get_filesystem(file_path, opener_options)

        file_names = [
            # extracting the filename could be done more robustly
            f.replace(fs_path, "").strip("/")
            for f in fs.listdir(fs_path, detail=False)
        ]

        meta = None
        if ML_META_FILENAME in file_names:
            try:
                with fs.open(f"{fs_path}/{ML_META_FILENAME}") as stream:
                    meta = parse_multi_level_dataset_meta(stream)
            except FileNotFoundError:
                pass

        level_0_path = None
        if "0.link" in file_names:
            try:
                with fs.open(f"{fs_path}/0.link") as stream:
                    level_0_path = stream.read()
            except FileNotFoundError:
                pass

        level_names, num_levels = parse_levels(file_names, level_0_path)

        engine = opener_options.pop("engine", "zarr")

        level_datasets: list[xr.Dataset | None] = []
        for level, level_name in level_names.items():
            level_path = f"{file_path}/{level_name}"
            level_dataset = xr.open_dataset(level_path, engine=engine, **opener_options)
            level_datasets.append((level_dataset, level_path))

        for level, (level_dataset, _) in enumerate(level_datasets):
            set_dataset_level_info(
                level_dataset,
                LevelInfo(
                    level=level,
                    num_levels=num_levels,
                    meta=meta,
                    datasets=level_datasets,
                ),
            )

        return level_datasets

    def postprocess(
        self, messages: list[list[Message]], file_path: str
    ) -> list[Message]:
        return list(itertools.chain(*messages))


def get_filesystem(file_path: str, opener_options: dict[str, Any]):
    storage_options = (
        opener_options.get(
            "storage_options",
            opener_options.get("backend_kwargs", {}).get("storage_options"),
        )
        or {}
    )
    _fs, fs_path = fsspec.core.url_to_fs(file_path, **storage_options)
    fs: fsspec.AbstractFileSystem = _fs
    fs_path: str = fs_path.replace("\\", "/")
    return fs, fs_path


def parse_levels(
    file_names: list[str], level_0_path: str | None
) -> tuple[dict[int, str], int]:
    level_names: dict[int, str] = {0: level_0_path} if level_0_path else {}
    num_levels = 0
    for file_name in file_names:
        m = level_pattern.match(file_name)
        if m is not None:
            level = int(m.group(1))
            level_names[level] = file_name
            num_levels = max(num_levels, level + 1)
    if not level_names:
        raise ValueError("empty multi-level dataset")
    num_levels = max(level_names.keys()) + 1
    for level in range(num_levels):
        if level not in level_names:
            raise ValueError(
                f"missing dataset for level {level} in multi-level dataset"
            )
    return level_names, num_levels


def parse_multi_level_dataset_meta(stream: Any) -> MultiLevelDatasetMeta:
    meta_content = json.load(stream)

    msg_prefix = f"illegal xcube {ML_META_FILENAME!r} file"

    if not isinstance(meta_content, dict):
        raise ValueError(f"{msg_prefix}, JSON object expected")

    version = meta_content.get("version")
    if not isinstance(version, str) or not version.startswith("1."):
        raise ValueError(f"{msg_prefix}, missing or invalid 'version'")

    num_levels = meta_content.get("num_levels")
    if not isinstance(num_levels, int) or num_levels < 1:
        raise ValueError(f"{msg_prefix}, missing or invalid 'num_levels'")

    return MultiLevelDatasetMeta(**meta_content)
