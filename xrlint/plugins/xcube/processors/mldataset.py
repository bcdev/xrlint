#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

import itertools
import json
import re
from typing import Any

import fsspec
import xarray as xr

from xrlint.plugins.xcube.constants import ML_FILE_PATTERN, ML_META_FILENAME
from xrlint.plugins.xcube.plugin import plugin
from xrlint.plugins.xcube.util import (
    LevelsMeta,
    attach_dataset_level_infos,
    resolve_path,
)
from xrlint.processor import ProcessorOp
from xrlint.result import Message

level_pattern = re.compile(r"^(\d+)(?:\.zarr)?$")
link_pattern = re.compile(r"^(\d+)(?:\.link)?$")


@plugin.define_processor("multi-level-dataset")
class MultiLevelDatasetProcessor(ProcessorOp):
    f"""This processor should be used with `files: [{ML_FILE_PATTERN}"]`."""

    def preprocess(
        self, file_path: str, opener_options: dict[str, Any]
    ) -> list[tuple[xr.Dataset | xr.DataTree, str]]:
        fs, fs_path = get_filesystem(file_path, opener_options)

        file_names = [
            # extracting the filename could be done more robustly
            f.replace(fs_path, "").strip("/")
            for f in fs.listdir(fs_path, detail=False)
        ]

        # check for optional ".zlevels" that provides meta-info
        meta = None
        if ML_META_FILENAME in file_names:
            with fs.open(f"{fs_path}/{ML_META_FILENAME}") as stream:
                meta = LevelsMeta.from_value(json.load(stream))

        # check for optional ".zgroup"
        # if ".zgroup" in file_names:
        #     with fs.open(f"{fs_path}/.zgroup") as stream:
        #         group_props = json.load(stream)

        level_paths, num_levels = parse_levels(fs, file_path, file_names)

        engine = opener_options.pop("engine", "zarr")

        level_datasets: list[xr.Dataset | None] = []
        for level, level_path in level_paths.items():
            level_dataset = xr.open_dataset(level_path, engine=engine, **opener_options)
            level_datasets.append((level_dataset, level_path))

        attach_dataset_level_infos(level_datasets, meta=meta)

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
    fs: fsspec.AbstractFileSystem, dataset_path: str, file_names: list[str]
) -> tuple[dict[int, str], int]:
    level_paths: dict[int, str] = {}
    for file_name in file_names:
        # check for optional "<level>.link" that locates a level somewhere else
        m = link_pattern.match(file_name)
        if m is not None:
            level = int(m.group(1))
            link_path = fs.read_text(f"{dataset_path}/{file_name}")
            level_paths[level] = resolve_path(link_path, root_path=dataset_path)
        # check for regular "<level>.zarr"
        m = level_pattern.match(file_name)
        if m is not None:
            level = int(m.group(1))
            level_paths[level] = f"{dataset_path}/{file_name}"

    if not level_paths:
        raise ValueError("empty multi-level dataset")

    num_levels = max(level_paths.keys()) + 1
    for level in range(num_levels):
        if level not in level_paths:
            raise ValueError(
                f"missing dataset for level {level} in multi-level dataset"
            )

    return level_paths, num_levels
