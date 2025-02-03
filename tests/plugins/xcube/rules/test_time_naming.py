#  Copyright © 2025 Brockmann Consult GmbH.
#  This software is distributed under the terms and conditions of the
#  MIT license (https://mit-license.org/).

import numpy as np
import xarray as xr

from xrlint.plugins.xcube.rules.time_naming import TimeNaming
from xrlint.testing import RuleTest, RuleTester


def make_dataset(time_var: str, time_dim: str | None = None):
    time_dim = time_dim or time_var
    dims = [time_dim, "y", "x"]
    n = 3
    return xr.Dataset(
        attrs=dict(title="v-data"),
        coords={
            "x": xr.DataArray(np.linspace(0, 1, n), dims="x", attrs={"units": "m"}),
            "y": xr.DataArray(np.linspace(0, 1, n), dims="y", attrs={"units": "m"}),
            time_var: xr.DataArray(
                list(range(n)),
                dims=time_dim,
                attrs={"units": "days since 2010-05-01 UTC", "calendar": "gregorian"},
            ),
        },
        data_vars={
            "chl": xr.DataArray(
                np.random.random((n, n, n)), dims=dims, attrs={"units": "mg/m^-3"}
            ),
            "tsm": xr.DataArray(
                np.random.random((n, n, n)), dims=dims, attrs={"units": "mg/m^-3"}
            ),
        },
    )


valid_dataset_0 = xr.Dataset()
valid_dataset_1 = make_dataset("time")

# Not ok, because time coord not called time
invalid_dataset_0 = make_dataset("t")

# Not ok, because no units
invalid_dataset_1 = make_dataset("time")
del invalid_dataset_1.time.attrs["units"]

# Not ok, because no calendar
invalid_dataset_2 = make_dataset("time")
del invalid_dataset_2.time.attrs["calendar"]

# Not ok, because invalid unit
invalid_dataset_3 = make_dataset("time")
invalid_dataset_3.time.attrs["units"] = "meters"

# Not ok, because coordinate 'time' should have dim 'time'
invalid_dataset_4 = make_dataset("time", "t0")

# Not ok, because coordinate 't0' should be named 'time'
invalid_dataset_5 = make_dataset("t0", "time")

TimeNamingTest = RuleTester.define_test(
    "time-naming",
    TimeNaming,
    valid=[
        RuleTest(dataset=valid_dataset_0),
        RuleTest(dataset=valid_dataset_1),
    ],
    invalid=[
        RuleTest(dataset=invalid_dataset_0, expected=1),
        RuleTest(dataset=invalid_dataset_1, expected=1),
        RuleTest(dataset=invalid_dataset_2, expected=1),
        RuleTest(dataset=invalid_dataset_3, expected=1),
        RuleTest(dataset=invalid_dataset_4, expected=1),
        RuleTest(dataset=invalid_dataset_5, expected=2),
    ],
)
