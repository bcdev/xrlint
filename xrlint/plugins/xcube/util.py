#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

from collections.abc import Hashable
from dataclasses import dataclass

import xarray as xr

from xrlint.util.constructible import MappingConstructible

from .constants import LAT_NAME, LON_NAME, ML_INFO_ATTR, X_NAME, Y_NAME


@dataclass(frozen=True, kw_only=True)
class LevelsMeta(MappingConstructible):
    """The contents of a xcube `.zlevels` meta-info file."""

    version: str
    num_levels: int
    tile_size: tuple[int, int] | None = None
    use_saved_levels: bool | None = None
    agg_methods: dict[str, str] | None = None


@dataclass(frozen=True, kw_only=True)
class LevelInfo:
    """Level info added to each level dataset to allow for validation
    of multi-level datasets.

    Note, this need to be aligned with
    <https://xcube.readthedocs.io/en/latest/mldatasets.html#the-xcube-levels-format>
    """

    level: int
    """Current level index."""

    num_levels: int
    """Actual number of levels found."""

    datasets: list[tuple[xr.Dataset, str]]
    """A list of num_levels pairs comprising
     level dataset and level file path.
     """

    meta: LevelsMeta | None = None
    """Content of a `.zlevels` file, if file was found."""


def get_dataset_level_info(dataset: xr.Dataset) -> LevelInfo | None:
    return dataset.attrs.get(ML_INFO_ATTR)


def set_dataset_level_info(dataset: xr.Dataset, level_info: LevelInfo):
    dataset.attrs[ML_INFO_ATTR] = level_info


def attach_dataset_level_infos(
    level_datasets: list[tuple[xr.Dataset, str]],
    meta: LevelsMeta | None = None,
):
    for level, (level_dataset, _) in enumerate(level_datasets):
        set_dataset_level_info(
            level_dataset,
            LevelInfo(
                level=level,
                num_levels=len(level_datasets),
                meta=meta,
                datasets=level_datasets,
            ),
        )


def is_spatial_var(var: xr.DataArray) -> bool:
    """Return 'True' if `var` looks like a spatial 2+d variable."""
    if var.ndim < 2:
        return False
    y_name, x_name = var.dims[-2:]
    return (x_name == X_NAME and y_name == Y_NAME) or (
        x_name == LON_NAME and y_name == LAT_NAME
    )


def get_spatial_size(
    dataset: xr.Dataset,
) -> tuple[tuple[Hashable, int], tuple[Hashable, int]] | None:
    """Return (x_size, y_size) for given dataset."""
    for k, v in dataset.data_vars.items():
        if is_spatial_var(v):
            y_name, x_name = v.dims[-2:]
            x_size = dataset.sizes[x_name]
            y_size = dataset.sizes[y_name]
            if x_size and y_size:
                return (x_name, x_size), (y_name, y_size)
    return None


def resolve_path(path: str, root_path: str | None = None) -> str:
    abs_level_path = path
    if root_path is not None and not is_absolute_path(path):
        abs_level_path = f"{root_path}/{path}"
    parts = abs_level_path.rstrip("/").replace("\\", "/").split("/")
    return "/".join(
        p
        for i, p in enumerate(parts)
        if p not in (".", "..") and (i == len(parts) - 1 or parts[i + 1] != "..")
    )


def is_absolute_path(path: str) -> bool:
    return (
        # Unix abs path
        path.startswith("/")
        # URL
        or "://" in path
        # Windows abs paths
        or path.startswith("\\\\")
        or path.find(":\\", 1) == 1
        or path.find(":/", 1) == 1
    )
