import numpy as np

from xrlint.plugins.xcube.rules.lat_lon_naming import LatLonNaming

import xarray as xr

from xrlint.testing import RuleTester, RuleTest


def make_dataset(lat_dim: str, lon_dim: str):
    dims = ["time", lat_dim, lon_dim]
    n = 3
    return xr.Dataset(
        attrs=dict(title="v-data"),
        coords={
            lon_dim: xr.DataArray(
                np.linspace(0, 1, n), dims=lon_dim, attrs={"units": "m"}
            ),
            lat_dim: xr.DataArray(
                np.linspace(0, 1, n), dims=lat_dim, attrs={"units": "m"}
            ),
            "time": xr.DataArray(
                list(range(2010, 2010 + n)), dims="time", attrs={"units": "years"}
            ),
        },
        data_vars={
            "chl": xr.DataArray(
                np.random.random((n, n, n)), dims=dims, attrs={"units": "mg/m^-3"}
            ),
            "tsm": xr.DataArray(
                np.random.random((n, n, n)), dims=dims, attrs={"units": "mg/m^-3"}
            ),
            "avg_temp": xr.DataArray(
                np.random.random(n), dims=dims[0], attrs={"units": "kelvin"}
            ),
            "mask": xr.DataArray(np.random.random((n, n)), dims=dims[-2:]),
        },
    )


valid_dataset_1 = make_dataset("lat", "lon")

invalid_dataset_1 = make_dataset("lat", "long")
invalid_dataset_2 = make_dataset("lat", "longitude")
invalid_dataset_3 = make_dataset("lat", "Lon")

invalid_dataset_4 = make_dataset("ltd", "lon")
invalid_dataset_5 = make_dataset("latitude", "lon")
invalid_dataset_6 = make_dataset("Lat", "lon")

LatLonNamingTest = RuleTester.define_test(
    "lat-lon-naming",
    LatLonNaming,
    valid=[
        RuleTest(dataset=valid_dataset_1),
    ],
    invalid=[
        RuleTest(dataset=invalid_dataset_1),
        RuleTest(dataset=invalid_dataset_2),
        RuleTest(dataset=invalid_dataset_3),
        RuleTest(dataset=invalid_dataset_4),
        RuleTest(dataset=invalid_dataset_5),
        RuleTest(dataset=invalid_dataset_6),
    ],
)
