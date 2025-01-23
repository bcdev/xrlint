from collections.abc import Hashable
from dataclasses import dataclass

import xarray as xr

from .constants import LAT_NAME, LON_NAME, X_NAME, Y_NAME, ML_INFO_ATTR


@dataclass(frozen=True, kw_only=True)
class MultiLevelDatasetMeta:
    version: str
    num_levels: int
    use_saved_levels: bool | None = None
    agg_methods: dict[str, str] | None = None


@dataclass(frozen=True, kw_only=True)
class LevelInfo:
    level: int
    num_levels: int
    datasets: list[tuple[xr.Dataset, str]]
    meta: MultiLevelDatasetMeta | None = None


def get_dataset_level_info(dataset: xr.Dataset) -> LevelInfo | None:
    return dataset.attrs.get(ML_INFO_ATTR)


def set_dataset_level_info(dataset: xr.Dataset, level_info: LevelInfo):
    dataset.attrs[ML_INFO_ATTR] = level_info


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


def get_spatial_size_for_dims(
    dataset: xr.Dataset, x_name: str, y_name: str
) -> tuple[int, int]:
    """Return (x_size, y_size) for given dataset and dim names."""
    x_size: int = 0
    y_size: int = 0
    for k, v in dataset.sizes.items():
        if k == x_name:
            x_size = v
        elif k == y_name:
            y_size = v
    return x_size, y_size
