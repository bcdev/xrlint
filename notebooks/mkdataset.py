import numpy as np
import xarray as xr

nx = 2
ny = 3
nt = 4


def make_dataset() -> xr.Dataset:
    """Create a dataset that passes xrlint core rules."""

    return xr.Dataset(
        attrs=dict(title="SST-Climatology Subset"),
        coords={
            "x": xr.DataArray(
                np.linspace(-180, 180, nx), dims="x", attrs={"units": "degrees"}
            ),
            "y": xr.DataArray(
                np.linspace(-90, 90, ny), dims="y", attrs={"units": "degrees"}
            ),
            "time": xr.DataArray(
                [2010 + y for y in range(nt)], dims="time", attrs={"units": "years"}
            ),
            "spatial_ref": xr.DataArray(
                0,
                attrs={
                    "grid_mapping_name": "latitude_longitude",
                    "semi_major_axis": 6371000.0,
                    "inverse_flattening": 0,
                },
            ),
        },
        data_vars={
            "sst": xr.DataArray(
                np.random.random((nt, ny, nx)),
                dims=["time", "y", "x"],
                attrs={"units": "kelvin", "grid_mapping": "spatial_ref"},
            ),
            "sst_anomaly": xr.DataArray(
                np.random.random((nt, ny, nx)),
                dims=["time", "y", "x"],
                attrs={"units": "kelvin", "grid_mapping": "spatial_ref"},
            ),
        },
    )


def make_dataset_with_issues() -> xr.Dataset:
    """Create a dataset that produces issues with xrlint core rules."""
    invalid_ds = make_dataset()
    invalid_ds.attrs = {}
    invalid_ds.sst.attrs["units"] = 1
    invalid_ds["sst_avg"] = xr.DataArray(
        np.random.random((nx, ny)), dims=["x", "y"], attrs={"units": "kelvin"}
    )
    return invalid_ds
