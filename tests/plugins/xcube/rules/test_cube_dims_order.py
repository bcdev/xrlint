import numpy as np

from xrlint.plugins.xcube.rules.cube_dims_order import CubeDimsOrder

import xarray as xr

from xrlint.testing import RuleTester, RuleTest


def make_dataset(dims: tuple[str, str, str]):
    n = 3
    return xr.Dataset(
        attrs=dict(title="v-data"),
        coords={
            "x": xr.DataArray(np.linspace(0, 1, n), dims="x", attrs={"units": "m"}),
            "y": xr.DataArray(np.linspace(0, 1, n), dims="y", attrs={"units": "m"}),
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
        },
    )


valid_dataset_1 = make_dataset(("time", "y", "x"))
valid_dataset_2 = make_dataset(("time", "lat", "lon"))
valid_dataset_3 = make_dataset(("level", "y", "x"))

invalid_dataset_1 = make_dataset(("time", "x", "y"))
invalid_dataset_2 = make_dataset(("x", "y", "time"))
invalid_dataset_3 = make_dataset(("time", "lon", "lat"))
invalid_dataset_4 = make_dataset(("lon", "lat", "level"))
invalid_dataset_5 = make_dataset(("x", "y", "level"))


CubeDimsOrderTest = RuleTester.define_test(
    "cube-dims-order",
    CubeDimsOrder,
    valid=[
        RuleTest(dataset=valid_dataset_1),
        RuleTest(dataset=valid_dataset_2),
        RuleTest(dataset=valid_dataset_3),
    ],
    invalid=[
        RuleTest(dataset=invalid_dataset_1),
        RuleTest(dataset=invalid_dataset_2),
        RuleTest(dataset=invalid_dataset_3),
        RuleTest(dataset=invalid_dataset_4),
        RuleTest(dataset=invalid_dataset_5),
    ],
)
