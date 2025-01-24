import math

import numpy as np
import xarray as xr


def make_cube_levels(nx: int, ny: int, nt: int, nl: int) -> list[xr.Dataset]:
    return [
        make_cube(math.ceil(nx >> level), math.ceil(ny >> level), nt)
        for level in range(nl)
    ]


def make_cube(nx: int, ny: int, nt: int) -> xr.Dataset:
    """Make an in-memory dataset that should pass all xcube rules.

    Args:
        nx: length of the lon-dimension
        ny: length of the lat-dimension
        nt: length of the time-dimension

    Returns:
        an in-memory dataset with one 3-d data variable "chl"
            with dimensions "time", "lat", "lon".
    """
    dx = 180.0 / nx
    dy = 90.0 / ny
    return xr.Dataset(
        coords=dict(
            lon=xr.DataArray(
                np.linspace(-180 + dx, 180 - dx, nx),
                dims="lon",
                attrs=dict(
                    long_name="longitude",
                    standard_name="longitude",
                    units="degrees_east",
                ),
            ),
            lat=xr.DataArray(
                np.linspace(-90 + dy, 90 - dy, ny),
                dims="lat",
                attrs=dict(
                    long_name="latitude",
                    standard_name="latitude",
                    units="degrees_north",
                ),
            ),
            time=xr.DataArray(
                range(nt),
                dims="time",
                attrs=dict(
                    long_name="time",
                    standard_name="time",
                    units="days since 2024-06-10:12:00:00 utc",
                    calendar="gregorian",
                ),
            ),
        ),
        data_vars=dict(
            chl=xr.DataArray(
                np.zeros((nt, ny, nx)),
                dims=["time", "lat", "lon"],
                attrs=dict(
                    long_name="chlorophyll concentration",
                    standard_name="chlorophyll_concentration",
                    units="mg/m^3",
                    _FillValue=0,
                ),
            ).chunk(time=1, lat=min(ny, 90), lon=min(nx, 90)),
        ),
        attrs=dict(),
    )
