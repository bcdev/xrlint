import numpy as np

from xrlint.plugins.xcube.rules.increasing_time import IncreasingTime

import xarray as xr

from xrlint.testing import RuleTester, RuleTest


def make_dataset():
    dims = ["time", "y", "x"]
    n = 5
    return xr.Dataset(
        attrs=dict(title="v-data"),
        coords={
            dims[2]: xr.DataArray(
                np.linspace(0, 1, n), dims=dims[2], attrs={"units": "m"}
            ),
            dims[1]: xr.DataArray(
                np.linspace(0, 1, n), dims=dims[1], attrs={"units": "m"}
            ),
            dims[0]: xr.DataArray(
                [2010, 2011, 2012, 2013, 2014],
                dims=dims[0],
                attrs={"units": "years"},
            ),
        },
        data_vars={
            "chl": xr.DataArray(
                np.random.random((n, n, n)), dims=dims, attrs={"units": "mg/m^-3"}
            ),
            "tsm": xr.DataArray(
                np.random.random((n, n, n)), dims=dims, attrs={"units": "mg/m^-3"}
            ),
            "mask": xr.DataArray(np.random.random((n, n)), dims=dims[-2:]),
        },
    )


valid_dataset_1 = make_dataset()

invalid_dataset_1 = make_dataset()
invalid_dataset_1 = invalid_dataset_1.assign_coords(
    time=xr.DataArray(
        [2010, 2011, 2012, 2013, 2013], dims="time", attrs={"units": "years"}
    )
)

invalid_dataset_2 = make_dataset()
invalid_dataset_2 = invalid_dataset_2.assign_coords(
    time=xr.DataArray(
        [2010, 2011, 2012, 2014, 2013], dims="time", attrs={"units": "years"}
    )
)

LatLonNamingTest = RuleTester.define_test(
    "increasing-time",
    IncreasingTime,
    valid=[
        RuleTest(dataset=valid_dataset_1),
    ],
    invalid=[
        RuleTest(dataset=invalid_dataset_1),
        RuleTest(dataset=invalid_dataset_2),
    ],
)
