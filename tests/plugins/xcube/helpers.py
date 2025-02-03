#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

import math

import numpy as np
import xarray as xr

from xrlint.plugins.xcube.util import LevelsMeta, attach_dataset_level_infos


def make_cube_levels(
    nl: int,
    nx: int,
    ny: int,
    nt: int | None = None,
    meta: LevelsMeta | None = None,
    force_infos: bool = False,
) -> list[xr.Dataset]:
    levels = [
        make_cube(math.ceil(nx >> level), math.ceil(ny >> level), nt)
        for level in range(nl)
    ]
    if meta is not None or force_infos:
        attach_dataset_level_infos(
            [(ds, f"{i}.zarr") for i, ds in enumerate(levels)], meta=meta
        )
    return levels


def make_cube(nx: int, ny: int, nt: int | None = None) -> xr.Dataset:
    """Make an in-memory dataset that should pass all xcube rules.

    Args:
        nx: length of the lon-dimension
        ny: length of the lat-dimension
        nt: length of the time-dimension, optional

    Returns:
        an in-memory dataset with one 3-d data variable "chl"
            with dimensions ["time",] "lat", "lon".
    """
    x_attrs = dict(
        long_name="longitude",
        standard_name="longitude",
        units="degrees_east",
    )
    y_attrs = dict(
        long_name="latitude",
        standard_name="latitude",
        units="degrees_north",
    )

    dx = 180.0 / nx
    dy = 90.0 / ny
    x_data = np.linspace(-180 + dx, 180 - dx, nx)
    y_data = np.linspace(-90 + dy, 90 - dy, ny)

    chl_attrs = dict(
        long_name="chlorophyll concentration",
        standard_name="chlorophyll_concentration",
        units="mg/m^3",
        _FillValue=0,
    )
    chl_chunks = dict(lat=min(ny, 90), lon=min(nx, 90))

    ds_attrs = dict(title="Chlorophyll")

    coords = dict(
        lon=xr.DataArray(x_data, dims="lon", attrs=x_attrs),
        lat=xr.DataArray(y_data, dims="lat", attrs=y_attrs),
    )

    if nt is None:
        return xr.Dataset(
            data_vars=dict(
                chl=xr.DataArray(
                    np.zeros((ny, nx)), dims=["lat", "lon"], attrs=chl_attrs
                ).chunk(**chl_chunks),
            ),
            coords=coords,
            attrs=ds_attrs,
        )
    else:
        time_attrs = dict(
            long_name="time",
            standard_name="time",
            units="days since 2024-06-10:12:00:00 utc",
            calendar="gregorian",
        )
        coords.update(time=xr.DataArray(range(nt), dims="time", attrs=time_attrs))
        return xr.Dataset(
            data_vars=dict(
                chl=xr.DataArray(
                    np.zeros((nt, ny, nx)), dims=["time", "lat", "lon"], attrs=chl_attrs
                ).chunk(time=1, **chl_chunks),
            ),
            coords=coords,
            attrs=ds_attrs,
        )
